import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

export interface LocationPage {
  slug: string;
  title: string;
  description: string;
  state: string;
  locationFactor: number;
  avgLaborRate: string;
  majorCities: string[];
  date: string;
  author: string;
  keywords: string[];
  content: string;
}

export interface LocationPageWithHTML extends LocationPage {
  contentHtml: string;
}

const LOCATIONS_DIR = fs.existsSync(path.join(process.cwd(), 'content', 'locations'))
  ? path.join(process.cwd(), 'content', 'locations')
  : path.join(process.cwd(), '..', 'content', 'locations');

function parseLocationFile(filename: string): LocationPage | null {
  const slug = filename.replace(/\.md$/, '');
  const filePath = path.join(LOCATIONS_DIR, filename);

  try {
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const { data: frontmatter, content } = matter(fileContent);

    return {
      slug,
      title: frontmatter.title || '',
      description: frontmatter.description || '',
      state: frontmatter.state || '',
      locationFactor: frontmatter.locationFactor || 1.0,
      avgLaborRate: frontmatter.avgLaborRate || '',
      majorCities: frontmatter.majorCities || [],
      date: frontmatter.date || '2026-02-21',
      author: frontmatter.author || 'Ungouge Team',
      keywords: frontmatter.keywords || [],
      content,
    };
  } catch (err) {
    console.error(`Error parsing location ${filename}:`, err);
    return null;
  }
}

export function getAllLocations(): LocationPage[] {
  if (!fs.existsSync(LOCATIONS_DIR)) {
    console.warn(`Locations directory not found: ${LOCATIONS_DIR}`);
    return [];
  }

  const files = fs
    .readdirSync(LOCATIONS_DIR)
    .filter((f) => f.endsWith('.md') && f !== 'TEMPLATE.md');

  const locations = files
    .map(parseLocationFile)
    .filter((loc): loc is LocationPage => loc !== null)
    .sort((a, b) => a.title.localeCompare(b.title));

  return locations;
}

export function getAllLocationSlugs(): string[] {
  if (!fs.existsSync(LOCATIONS_DIR)) return [];
  return fs
    .readdirSync(LOCATIONS_DIR)
    .filter((f) => f.endsWith('.md') && f !== 'TEMPLATE.md')
    .map((f) => f.replace(/\.md$/, ''));
}

export async function getLocationBySlug(slug: string): Promise<LocationPageWithHTML | null> {
  const filename = `${slug}.md`;
  const location = parseLocationFile(filename);

  if (!location) return null;

  const processedContent = await remark()
    .use(html, { sanitize: false })
    .process(location.content);
  const contentHtml = processedContent.toString();

  return {
    ...location,
    contentHtml,
  };
}
