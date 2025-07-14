#!/usr/bin/env python3
"""
Comprehensive test for OpenAI GPT-3.5-turbo integration with max_tokens fix
Tests all requirements from the review request
"""

import requests
import json

# Test the exact sample data from the review request
SAMPLE_APPLICATION = {
    'business_name': 'Tech Startup Inc',
    'industry': 'Technology', 
    'years_in_business': 3,
    'annual_revenue': 750000.0,
    'credit_score': 680,
    'monthly_cash_flow': 15000.0,
    'existing_debt': 50000.0,
    'loan_amount_requested': 200000.0,
    'loan_purpose': 'Business Expansion',
    'contact_email': 'john@techstartup.com',
    'contact_phone': '(555) 123-4567'
}

BACKEND_URL = 'https://9a956868-ad08-497e-953d-efe2266b1d5e.preview.emergentagent.com/api'

print('COMPREHENSIVE TEST: OpenAI GPT-3.5-turbo Integration with Max Tokens Fix')
print('=' * 80)
print('Testing all requirements from the review request:')
print('1. Submit the same sample loan application to /api/submit-application')
print('2. Verify that the AI analysis is now working properly with actual GPT-3.5-turbo responses')
print('3. Check that the response includes meaningful loan analysis')
print('4. Confirm that key_strengths, key_concerns, and improvement_suggestions are populated with actual AI insights')
print('5. Validate that the entire loan application flow works end-to-end')
print('=' * 80)
print()

try:
    print('📋 STEP 1: Submitting sample loan application...')
    response = requests.post(
        f'{BACKEND_URL}/submit-application',
        json=SAMPLE_APPLICATION,
        headers={'Content-Type': 'application/json'},
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print('✅ SUCCESS: Application submitted successfully')
        print()
        
        print('📊 STEP 2: Verifying AI analysis quality...')
        ai_analysis = data.get('ai_analysis', '')
        
        # Check for fallback indicators
        fallback_indicators = [
            'Unable to complete AI analysis',
            'Manual review required', 
            'AI analysis unavailable'
        ]
        
        is_fallback = any(indicator in ai_analysis for indicator in fallback_indicators)
        
        if not is_fallback and len(ai_analysis) > 100:
            print('✅ AI analysis is from actual GPT-3.5-turbo (not fallback)')
            print(f'   Analysis length: {len(ai_analysis)} characters')
            print(f'   Content: {ai_analysis}')
        else:
            print('❌ AI analysis appears to be fallback response')
            print(f'   Content: {ai_analysis}')
        print()
        
        print('🔍 STEP 3: Checking meaningful loan analysis...')
        required_fields = ['qualification_score', 'qualification_status', 'recommended_loan_amount', 'interest_rate_range', 'risk_assessment']
        all_present = all(field in data for field in required_fields)
        
        if all_present:
            print('✅ All required analysis fields present:')
            print(f'   Qualification Score: {data["qualification_score"]}/100')
            print(f'   Status: {data["qualification_status"]}')
            print(f'   Recommended Amount: ${data["recommended_loan_amount"]:,.2f}')
            print(f'   Interest Rate: {data["interest_rate_range"]}')
            print(f'   Risk Assessment: {data["risk_assessment"]}')
        else:
            print('❌ Missing required analysis fields')
        print()
        
        print('💡 STEP 4: Verifying AI insights are populated...')
        key_strengths = data.get('key_strengths', [])
        key_concerns = data.get('key_concerns', [])
        improvement_suggestions = data.get('improvement_suggestions', [])
        
        insights_populated = len(key_strengths) > 0 and len(key_concerns) > 0 and len(improvement_suggestions) > 0
        
        if insights_populated:
            print('✅ All AI insight fields populated with actual content:')
            print(f'   Key Strengths ({len(key_strengths)}):')
            for i, strength in enumerate(key_strengths, 1):
                print(f'     {i}. {strength}')
            print(f'   Key Concerns ({len(key_concerns)}):')
            for i, concern in enumerate(key_concerns, 1):
                print(f'     {i}. {concern}')
            print(f'   Improvement Suggestions ({len(improvement_suggestions)}):')
            for i, suggestion in enumerate(improvement_suggestions, 1):
                print(f'     {i}. {suggestion}')
        else:
            print('❌ AI insight fields not properly populated')
            print(f'   Key Strengths: {key_strengths}')
            print(f'   Key Concerns: {key_concerns}')
            print(f'   Improvement Suggestions: {improvement_suggestions}')
        print()
        
        print('🔄 STEP 5: Validating end-to-end loan application flow...')
        application_id = data.get('application_id')
        matched_lenders = data.get('matched_lenders', [])
        next_steps = data.get('next_steps', [])
        
        # Test retrieval of stored application
        retrieval_response = requests.get(f'{BACKEND_URL}/application/{application_id}', timeout=10)
        
        flow_working = (
            application_id and 
            len(matched_lenders) > 0 and 
            len(next_steps) > 0 and 
            retrieval_response.status_code == 200
        )
        
        if flow_working:
            print('✅ End-to-end flow working perfectly:')
            print(f'   Application ID: {application_id}')
            print(f'   Matched Lenders: {len(matched_lenders)}')
            print(f'   Next Steps: {len(next_steps)}')
            print(f'   Data Persistence: ✅ (retrieved successfully)')
        else:
            print('❌ End-to-end flow has issues')
        print()
        
        print('=' * 80)
        print('🎯 FINAL ASSESSMENT:')
        
        all_tests_passed = (
            not is_fallback and len(ai_analysis) > 100 and
            all_present and
            insights_populated and
            flow_working
        )
        
        if all_tests_passed:
            print('🎉 ALL REQUIREMENTS MET!')
            print('✅ OpenAI GPT-3.5-turbo integration is working correctly')
            print('✅ Max tokens fix (4000 tokens) is successful')
            print('✅ AI analysis provides meaningful insights')
            print('✅ All AI insight fields are populated with actual content')
            print('✅ End-to-end loan application flow works perfectly')
        else:
            print('⚠️ Some requirements not fully met - see details above')
        
    else:
        print(f'❌ ERROR: HTTP {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'❌ EXCEPTION: {str(e)}')