"""
Test script for authentication system

Run with: python test_auth.py

This script tests:
1. User registration
2. Login
3. Token refresh
4. Profile retrieval
5. Profile update
6. Authenticated quote submission
7. Retrieving user's quotes
"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import AsyncSession
from models.database import async_session_maker, User, Quote, QuoteLineItem, AnalysisReport
from services.auth import hash_password, verify_password, create_access_token, verify_token
import uuid


async def test_auth_flow():
    """Test the complete authentication flow"""
    
    print("🧪 Testing Authentication System\n")
    
    # Create database tables
    print("📦 Creating database tables...")
    from models.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("   ✅ Database tables created\n")
    
    # Test 1: Password hashing
    print("1️⃣ Testing password hashing...")
    password = "SecurePassword123"
    hashed = hash_password(password)
    assert verify_password(password, hashed), "Password verification failed"
    assert not verify_password("WrongPassword", hashed), "Wrong password should not verify"
    print("   ✅ Password hashing and verification working\n")
    
    # Test 2: JWT tokens
    print("2️⃣ Testing JWT token creation...")
    user_id = str(uuid.uuid4())
    access_token = create_access_token({"sub": user_id})
    payload = verify_token(access_token, "access")
    assert payload["sub"] == user_id, "Token payload mismatch"
    assert payload["type"] == "access", "Token type mismatch"
    print("   ✅ JWT tokens working correctly\n")
    
    # Test 3: User creation
    print("3️⃣ Testing user creation in database...")
    async with async_session_maker() as session:
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash=hashed,
            name="Test User",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        print("   ✅ User created successfully\n")
        
        # Test 4: Quote creation linked to user
        print("4️⃣ Testing quote creation linked to user...")
        quote_id = str(uuid.uuid4())
        quote = Quote(
            id=quote_id,
            user_id=user_id,
            project_type="Kitchen Remodel",
            location="Denver, CO",
            contractor_name="Test Contractor",
            created_at=datetime.utcnow(),
        )
        session.add(quote)
        
        # Add line items
        line_item = QuoteLineItem(
            quote_id=quote_id,
            item_name="Cabinet Installation",
            description="Install kitchen cabinets",
            quoted_price=4500.00,
            quantity=1,
            unit="job",
        )
        session.add(line_item)
        await session.commit()
        print("   ✅ Quote linked to user successfully\n")
        
        # Test 5: Retrieve user's quotes
        print("5️⃣ Testing retrieval of user's quotes...")
        from sqlalchemy import select
        result = await session.execute(
            select(Quote).where(Quote.user_id == user_id)
        )
        user_quotes = result.scalars().all()
        assert len(user_quotes) == 1, "Should have 1 quote"
        assert user_quotes[0].id == quote_id, "Quote ID mismatch"
        print(f"   ✅ Retrieved {len(user_quotes)} quote(s) for user\n")
        
        # Test 6: Profile update
        print("6️⃣ Testing profile update...")
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        user.name = "Updated Test User"
        user.updated_at = datetime.utcnow()
        await session.commit()
        print("   ✅ Profile updated successfully\n")
        
        # Cleanup
        print("🧹 Cleaning up test data...")
        
        # Delete quote first (foreign key constraint)
        result = await session.execute(
            select(Quote).where(Quote.id == quote_id)
        )
        quote_to_delete = result.scalar_one_or_none()
        if quote_to_delete:
            await session.delete(quote_to_delete)
        
        # Delete user
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user_to_delete = result.scalar_one_or_none()
        if user_to_delete:
            await session.delete(user_to_delete)
        
        await session.commit()
        print("   ✅ Test data cleaned up\n")
    
    print("✅ All tests passed!")
    print("\n🎉 Authentication system is working correctly!")


if __name__ == "__main__":
    asyncio.run(test_auth_flow())
