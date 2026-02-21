import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

export interface BlogPost {
  slug: string;
  title: string;
  description: string;
  date: string;
  author: string;
  keywords: string[];
  content: string; // raw markdown (without frontmatter)
  excerpt: string;
  readingTime: number; // minutes
}

export interface BlogPostWithHTML extends BlogPost {
  contentHtml: string;
}

// Blog posts live in the content/blog directory
// Try local content first (inside frontend/), then parent directory
const BLOG_DIR = fs.existsSync(path.join(process.cwd(), 'content', 'blog'))
  ? path.join(process.cwd(), 'content', 'blog')
  : path.join(process.cwd(), '..', 'content', 'blog');

/**
 * Extract title from markdown content (first # heading)
 */
function extractTitleFromMarkdown(content: string): string {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : 'Untitled';
}

/**
 * Extract description from markdown content
 * Looks for *Meta Description: ...* pattern or first substantive paragraph
 */
function extractDescriptionFromMarkdown(content: string): string {
  // Try to find *Meta Description: ...*
  const metaDescMatch = content.match(/\*Meta Description:\s*(.+?)\*/);
  if (metaDescMatch) {
    return metaDescMatch[1].trim();
  }

  // Otherwise, find first paragraph that isn't a heading, metadata, or horizontal rule
  const lines = content.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (
      trimmed &&
      !trimmed.startsWith('#') &&
      !trimmed.startsWith('*') &&
      !trimmed.startsWith('---') &&
      !trimmed.startsWith('|') &&
      trimmed.length > 50
    ) {
      return trimmed.slice(0, 160) + (trimmed.length > 160 ? '...' : '');
    }
  }

  return '';
}

/**
 * Extract date from markdown content
 * Looks for *Published: ...* pattern
 */
function extractDateFromMarkdown(content: string): string {
  const match = content.match(/\*Published:\s*(.+?)\*/);
  if (match) {
    const dateStr = match[1].trim();
    try {
      return new Date(dateStr).toISOString().split('T')[0];
    } catch {
      // fall through
    }
  }
  // Default to a reasonable date
  return '2026-02-01';
}

/**
 * Calculate reading time from text
 */
function calculateReadingTime(text: string): number {
  const wordsPerMinute = 230;
  const words = text.trim().split(/\s+/).length;
  return Math.max(1, Math.ceil(words / wordsPerMinute));
}

/**
 * Generate excerpt from content
 */
function generateExcerpt(content: string, maxLength = 160): string {
  // Strip markdown syntax for a clean excerpt
  const cleaned = content
    .replace(/^#+\s+.+$/gm, '') // headings
    .replace(/\*{1,2}(.+?)\*{1,2}/g, '$1') // bold/italic
    .replace(/\[(.+?)\]\(.+?\)/g, '$1') // links
    .replace(/!\[.*?\]\(.+?\)/g, '') // images
    .replace(/`{1,3}[^`]*`{1,3}/g, '') // code
    .replace(/^\s*[-*]\s+/gm, '') // list items
    .replace(/^\s*\d+\.\s+/gm, '') // numbered lists
    .replace(/^\|.*\|$/gm, '') // tables
    .replace(/^---$/gm, '') // horizontal rules
    .replace(/\n{2,}/g, '\n')
    .trim();

  // Find first substantive paragraph
  const paragraphs = cleaned.split('\n').filter(
    (p) => p.trim().length > 30 && !p.startsWith('*')
  );

  const firstParagraph = paragraphs[0] || cleaned;
  if (firstParagraph.length <= maxLength) return firstParagraph;
  return firstParagraph.slice(0, maxLength).replace(/\s+\S*$/, '') + '...';
}

/**
 * Parse a single blog post file
 */
function parsePostFile(filename: string): BlogPost | null {
  const slug = filename.replace(/\.md$/, '');
  const filePath = path.join(BLOG_DIR, filename);

  try {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const { data: frontmatter, content } = matter(fileContent);

    // Determine if we have proper frontmatter
    const hasFrontmatter = frontmatter && Object.keys(frontmatter).length > 0 && frontmatter.title;

    const title = hasFrontmatter
      ? frontmatter.title
      : extractTitleFromMarkdown(content || fileContent);

    const description = hasFrontmatter
      ? frontmatter.description || ''
      : extractDescriptionFromMarkdown(content || fileContent);

    let date: string;
    if (hasFrontmatter && frontmatter.date) {
      // gray-matter may parse date as Date object
      date =
        frontmatter.date instanceof Date
          ? frontmatter.date.toISOString().split('T')[0]
          : String(frontmatter.date);
    } else {
      date = extractDateFromMarkdown(fileContent);
    }

    const author = hasFrontmatter ? frontmatter.author || 'Ungouge Team' : 'Ungouge Team';

    const keywords: string[] = hasFrontmatter
      ? (frontmatter.keywords || [])
      : [];

    const bodyContent = hasFrontmatter ? content : fileContent;
    const readingTime = calculateReadingTime(bodyContent);
    const excerpt = description || generateExcerpt(bodyContent);

    return {
      slug,
      title,
      description: description || excerpt,
      date,
      author,
      keywords,
      content: bodyContent,
      excerpt,
      readingTime,
    };
  } catch (err) {
    console.error(`Error parsing blog post ${filename}:`, err);
    return null;
  }
}

/**
 * Get post priority score for sorting (higher = more important)
 */
function getPostPriority(slug: string): number {
  // Tier 1: Core evaluation guides (highest priority)
  const tier1 = [
    '01-is-contractor-quote-too-high',
    'signs-your-contractor-is-overcharging',
    'how-to-read-contractor-quote',
    '03-contractor-quote-red-flags',
  ];
  if (tier1.includes(slug)) return 1000;

  // Tier 2: High-traffic cost guides
  const tier2 = [
    'roof-replacement-cost-guide-2026',
    '02-kitchen-remodel-cost-2026',
    'bathroom-remodel-cost-breakdown',
    'hvac-replacement-cost-breakdown',
    'hvac-quote-too-high-fair-pricing-2026',
  ];
  if (tier2.includes(slug)) return 900;

  // Tier 3: Supporting educational content
  const tier3 = [
    'fair-contractor-markup-2026',
    'how-to-spot-contractor-quote-padding',
    'when-to-walk-away-contractor-quote',
    'how-to-negotiate-contractor-quotes',
    'contractor-quote-vs-estimate',
    'do-i-need-3-contractor-quotes',
  ];
  if (tier3.includes(slug)) return 800;

  // Tier 4: Other cost breakdowns
  const tier4 = [
    'deck-building-cost-breakdown',
    'flooring-installation-cost-breakdown',
    'painting-cost-breakdown',
    'siding-installation-cost-breakdown',
    'window-replacement-cost-breakdown',
    'electrical-work-cost-breakdown',
    'basement-finishing-cost-breakdown',
  ];
  if (tier4.includes(slug)) return 700;

  // Default: everything else
  return 500;
}

/**
 * Get all blog posts, sorted by priority (most useful first)
 */
export function getAllPosts(): BlogPost[] {
  if (!fs.existsSync(BLOG_DIR)) {
    console.warn(`Blog directory not found: ${BLOG_DIR}`);
    return [];
  }

  const files = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith('.md'));

  const posts = files
    .map(parsePostFile)
    .filter((post): post is BlogPost => post !== null)
    .sort((a, b) => {
      // Sort by priority first
      const priorityDiff = getPostPriority(b.slug) - getPostPriority(a.slug);
      if (priorityDiff !== 0) return priorityDiff;
      
      // If same priority, sort by date (newest first)
      return new Date(b.date).getTime() - new Date(a.date).getTime();
    });

  return posts;
}

/**
 * Get all post slugs (for generateStaticParams)
 */
export function getAllPostSlugs(): string[] {
  if (!fs.existsSync(BLOG_DIR)) return [];
  return fs
    .readdirSync(BLOG_DIR)
    .filter((f) => f.endsWith('.md'))
    .map((f) => f.replace(/\.md$/, ''));
}

/**
 * Get a single post by slug with rendered HTML
 */
export async function getPostBySlug(slug: string): Promise<BlogPostWithHTML | null> {
  const filename = `${slug}.md`;
  const post = parsePostFile(filename);

  if (!post) return null;

  // Convert markdown to HTML
  const processedContent = await remark().use(html, { sanitize: false }).process(post.content);
  const contentHtml = processedContent.toString();

  return {
    ...post,
    contentHtml,
  };
}
