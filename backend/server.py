from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'quickflow_capital')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Pydantic models
class BusinessApplication(BaseModel):
    business_name: str
    industry: str
    years_in_business: int
    annual_revenue: float
    credit_score: int
    monthly_cash_flow: float
    existing_debt: float
    loan_amount_requested: float
    loan_purpose: str
    contact_email: str
    contact_phone: str

class LoanResult(BaseModel):
    application_id: str
    qualification_score: int
    qualification_status: str
    recommended_loan_amount: float
    interest_rate_range: str
    risk_assessment: str
    ai_analysis: str
    matched_lenders: List[dict]
    next_steps: List[str]

# Mock lender data
MOCK_LENDERS = [
    {
        "lender_name": "Capital Growth Partners",
        "lender_type": "Bank",
        "min_credit_score": 680,
        "max_loan_amount": 5000000,
        "interest_rate_range": "5.5% - 8.2%",
        "specialties": ["Manufacturing", "Technology", "Healthcare"]
    },
    {
        "lender_name": "SmallBiz Finance Co",
        "lender_type": "Alternative Lender",
        "min_credit_score": 620,
        "max_loan_amount": 2000000,
        "interest_rate_range": "7.2% - 12.5%",
        "specialties": ["Retail", "Food Service", "Professional Services"]
    },
    {
        "lender_name": "SBA Preferred Lending",
        "lender_type": "SBA Lender",
        "min_credit_score": 650,
        "max_loan_amount": 3500000,
        "interest_rate_range": "4.8% - 7.5%",
        "specialties": ["Construction", "Manufacturing", "Agriculture"]
    },
    {
        "lender_name": "Quick Capital Solutions",
        "lender_type": "Online Lender",
        "min_credit_score": 580,
        "max_loan_amount": 1500000,
        "interest_rate_range": "9.5% - 15.8%",
        "specialties": ["E-commerce", "Technology", "Marketing"]
    },
    {
        "lender_name": "Community First Bank",
        "lender_type": "Community Bank",
        "min_credit_score": 700,
        "max_loan_amount": 2500000,
        "interest_rate_range": "5.8% - 9.2%",
        "specialties": ["Local Business", "Real Estate", "Agriculture"]
    }
]

def calculate_debt_to_income_ratio(monthly_cash_flow: float, existing_debt: float) -> float:
    """Calculate debt-to-income ratio"""
    if monthly_cash_flow <= 0:
        return 999  # Very high ratio for negative cash flow
    monthly_debt_payment = existing_debt * 0.05  # Assume 5% monthly payment
    return (monthly_debt_payment / monthly_cash_flow) * 100

async def analyze_loan_application_with_ai(application: BusinessApplication) -> dict:
    """Use GPT-4o to analyze loan application"""
    
    # Calculate debt-to-income ratio
    debt_to_income = calculate_debt_to_income_ratio(application.monthly_cash_flow, application.existing_debt)
    
    # Create system message for loan analysis
    system_message = """You are an expert business loan underwriter with 20+ years of experience. 
    Analyze the provided business loan application and provide a comprehensive assessment.
    
    Provide your response in the following JSON format:
    {
        "qualification_score": <integer from 0-100>,
        "qualification_status": "<Approved/Conditional/Declined>",
        "recommended_loan_amount": <float>,
        "interest_rate_range": "<X.X% - X.X%>",
        "risk_assessment": "<Low/Medium/High>",
        "analysis_summary": "<detailed analysis in 2-3 sentences>",
        "key_strengths": ["<strength1>", "<strength2>"],
        "key_concerns": ["<concern1>", "<concern2>"],
        "improvement_suggestions": ["<suggestion1>", "<suggestion2>"]
    }
    
    Consider these factors:
    - Credit score impact (weight: 25%)
    - Cash flow stability (weight: 20%)
    - Years in business (weight: 15%)
    - Debt-to-income ratio (weight: 20%)
    - Industry risk (weight: 10%)
    - Loan amount vs revenue ratio (weight: 10%)
    """
    
    # Create user message with application details
    user_message_text = f"""
    Please analyze this business loan application:
    
    Business Details:
    - Business Name: {application.business_name}
    - Industry: {application.industry}
    - Years in Business: {application.years_in_business}
    - Annual Revenue: ${application.annual_revenue:,.2f}
    
    Financial Metrics:
    - Credit Score: {application.credit_score}
    - Monthly Cash Flow: ${application.monthly_cash_flow:,.2f}
    - Existing Debt: ${application.existing_debt:,.2f}
    - Debt-to-Income Ratio: {debt_to_income:.1f}%
    
    Loan Request:
    - Requested Amount: ${application.loan_amount_requested:,.2f}
    - Purpose: {application.loan_purpose}
    - Loan-to-Revenue Ratio: {(application.loan_amount_requested / application.annual_revenue * 100):.1f}%
    
    Provide a comprehensive loan analysis following the JSON format specified.
    """
    
    try:
        # Create chat instance
        session_id = f"loan_analysis_{uuid.uuid4()}"
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-3.5-turbo")
        
        # Send message to GPT-4o
        user_message = UserMessage(text=user_message_text)
        response = await chat.send_message(user_message)
        
        # Parse AI response (assuming it returns JSON)
        import json
        try:
            ai_analysis = json.loads(response)
        except json.JSONDecodeError:
            # Fallback if response is not JSON
            ai_analysis = {
                "qualification_score": 75,
                "qualification_status": "Conditional",
                "recommended_loan_amount": application.loan_amount_requested * 0.8,
                "interest_rate_range": "7.5% - 10.2%",
                "risk_assessment": "Medium",
                "analysis_summary": response[:200] + "...",
                "key_strengths": ["Business experience", "Positive cash flow"],
                "key_concerns": ["Credit score evaluation needed", "Industry analysis required"],
                "improvement_suggestions": ["Improve credit score", "Increase cash flow"]
            }
        
        return ai_analysis
        
    except Exception as e:
        print(f"AI analysis error: {e}")
        # Fallback analysis
        return {
            "qualification_score": 60,
            "qualification_status": "Conditional",
            "recommended_loan_amount": application.loan_amount_requested * 0.7,
            "interest_rate_range": "8.0% - 12.0%",
            "risk_assessment": "Medium",
            "analysis_summary": "Unable to complete AI analysis. Manual review required.",
            "key_strengths": ["Business established", "Revenue positive"],
            "key_concerns": ["AI analysis unavailable", "Manual review needed"],
            "improvement_suggestions": ["Contact loan officer", "Provide additional documentation"]
        }

def match_lenders(application: BusinessApplication, ai_analysis: dict) -> List[dict]:
    """Match business with appropriate lenders based on AI analysis"""
    matched_lenders = []
    
    for lender in MOCK_LENDERS:
        # Check credit score requirement
        if application.credit_score >= lender["min_credit_score"]:
            # Check loan amount capacity
            if application.loan_amount_requested <= lender["max_loan_amount"]:
                # Check industry match
                industry_match = application.industry in lender["specialties"]
                
                # Calculate match score
                match_score = 0
                if industry_match:
                    match_score += 30
                if application.credit_score >= lender["min_credit_score"] + 50:
                    match_score += 25
                if ai_analysis["qualification_score"] >= 80:
                    match_score += 20
                if ai_analysis["risk_assessment"] == "Low":
                    match_score += 15
                else:
                    match_score += 10
                
                matched_lenders.append({
                    "lender_name": lender["lender_name"],
                    "lender_type": lender["lender_type"],
                    "interest_rate_range": lender["interest_rate_range"],
                    "match_score": match_score,
                    "industry_match": industry_match,
                    "pre_approval_likelihood": "High" if match_score >= 70 else "Medium" if match_score >= 50 else "Low"
                })
    
    # Sort by match score
    matched_lenders.sort(key=lambda x: x["match_score"], reverse=True)
    return matched_lenders[:3]  # Return top 3 matches

@app.post("/api/submit-application")
async def submit_loan_application(application: BusinessApplication):
    """Submit and analyze loan application"""
    try:
        # Generate application ID
        application_id = str(uuid.uuid4())
        
        # Analyze with AI
        ai_analysis = await analyze_loan_application_with_ai(application)
        
        # Match with lenders
        matched_lenders = match_lenders(application, ai_analysis)
        
        # Generate next steps based on qualification
        next_steps = []
        if ai_analysis["qualification_status"] == "Approved":
            next_steps = [
                "Review matched lenders and their terms",
                "Prepare required documentation",
                "Schedule consultation with preferred lender",
                "Submit formal loan application"
            ]
        elif ai_analysis["qualification_status"] == "Conditional":
            next_steps = [
                "Address key concerns identified in analysis",
                "Gather additional financial documentation",
                "Consider improving credit score if needed",
                "Review matched lenders for best fit"
            ]
        else:
            next_steps = [
                "Review improvement suggestions",
                "Work on strengthening financial position",
                "Consider alternative financing options",
                "Reapply after addressing concerns"
            ]
        
        # Create loan result
        loan_result = {
            "application_id": application_id,
            "qualification_score": ai_analysis["qualification_score"],
            "qualification_status": ai_analysis["qualification_status"],
            "recommended_loan_amount": ai_analysis["recommended_loan_amount"],
            "interest_rate_range": ai_analysis["interest_rate_range"],
            "risk_assessment": ai_analysis["risk_assessment"],
            "ai_analysis": ai_analysis["analysis_summary"],
            "key_strengths": ai_analysis.get("key_strengths", []),
            "key_concerns": ai_analysis.get("key_concerns", []),
            "improvement_suggestions": ai_analysis.get("improvement_suggestions", []),
            "matched_lenders": matched_lenders,
            "next_steps": next_steps,
            "created_at": datetime.utcnow()
        }
        
        # Store in database
        application_data = {
            "application_id": application_id,
            "business_details": application.dict(),
            "loan_result": loan_result,
            "created_at": datetime.utcnow()
        }
        
        await db.loan_applications.insert_one(application_data)
        
        return loan_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing application: {str(e)}")

@app.get("/api/application/{application_id}")
async def get_application(application_id: str):
    """Get loan application results"""
    try:
        application = await db.loan_applications.find_one({"application_id": application_id})
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Remove MongoDB _id field
        application.pop('_id', None)
        return application
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving application: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "QuickFlow Capital API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)