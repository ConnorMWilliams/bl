import React, { useState } from 'react';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('form');
  const [formData, setFormData] = useState({
    business_name: '',
    industry: '',
    years_in_business: '',
    annual_revenue: '',
    credit_score: '',
    monthly_cash_flow: '',
    existing_debt: '',
    loan_amount_requested: '',
    loan_purpose: '',
    contact_email: '',
    contact_phone: ''
  });
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const industries = [
    'Technology', 'Healthcare', 'Manufacturing', 'Retail', 'Food Service',
    'Professional Services', 'Construction', 'Real Estate', 'Agriculture',
    'Transportation', 'E-commerce', 'Marketing', 'Education', 'Finance',
    'Entertainment', 'Other'
  ];

  const loanPurposes = [
    'Working Capital', 'Equipment Purchase', 'Business Expansion', 'Real Estate',
    'Inventory', 'Marketing', 'Debt Consolidation', 'Technology Upgrade',
    'Hiring Staff', 'Other'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Convert string numbers to actual numbers
      const processedData = {
        ...formData,
        years_in_business: parseInt(formData.years_in_business),
        annual_revenue: parseFloat(formData.annual_revenue),
        credit_score: parseInt(formData.credit_score),
        monthly_cash_flow: parseFloat(formData.monthly_cash_flow),
        existing_debt: parseFloat(formData.existing_debt),
        loan_amount_requested: parseFloat(formData.loan_amount_requested)
      };

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/submit-application`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(processedData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit application');
      }

      const result = await response.json();
      setResults(result);
      setCurrentStep('results');
    } catch (err) {
      setError('Error submitting application. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved': return 'bg-green-100 text-green-800';
      case 'Conditional': return 'bg-yellow-100 text-yellow-800';
      case 'Declined': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const resetForm = () => {
    setCurrentStep('form');
    setResults(null);
    setError('');
    setFormData({
      business_name: '',
      industry: '',
      years_in_business: '',
      annual_revenue: '',
      credit_score: '',
      monthly_cash_flow: '',
      existing_debt: '',
      loan_amount_requested: '',
      loan_purpose: '',
      contact_email: '',
      contact_phone: ''
    });
  };

  if (currentStep === 'results' && results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-xl overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
                <h1 className="text-3xl font-bold">Loan Prequalification Results</h1>
                <p className="text-blue-100 mt-2">AI-Powered Analysis Complete</p>
              </div>

              {/* Main Results */}
              <div className="p-6">
                {/* Qualification Score */}
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-800">Qualification Score</h2>
                      <p className="text-gray-600">Based on AI analysis of your business profile</p>
                    </div>
                    <div className="text-right">
                      <div className={`text-6xl font-bold ${getScoreColor(results.qualification_score)}`}>
                        {results.qualification_score}
                      </div>
                      <div className="text-2xl text-gray-500">/ 100</div>
                    </div>
                  </div>
                </div>

                {/* Status and Details */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Status</h3>
                    <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(results.qualification_status)}`}>
                      {results.qualification_status}
                    </span>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Risk Assessment</h3>
                    <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${
                      results.risk_assessment === 'Low' ? 'bg-green-100 text-green-800' :
                      results.risk_assessment === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {results.risk_assessment} Risk
                    </span>
                  </div>
                </div>

                {/* Loan Details */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Recommended Loan Amount</h3>
                    <div className="text-2xl font-bold text-green-600">
                      {formatCurrency(results.recommended_loan_amount)}
                    </div>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Interest Rate Range</h3>
                    <div className="text-2xl font-bold text-blue-600">
                      {results.interest_rate_range}
                    </div>
                  </div>
                </div>

                {/* AI Analysis */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-blue-800 mb-3">AI Analysis Summary</h3>
                  <p className="text-blue-700">{results.ai_analysis}</p>
                </div>

                {/* Strengths and Concerns */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-green-800 mb-3">Key Strengths</h3>
                    <ul className="space-y-2">
                      {results.key_strengths?.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-600 mr-2">✓</span>
                          <span className="text-green-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-yellow-800 mb-3">Key Concerns</h3>
                    <ul className="space-y-2">
                      {results.key_concerns?.map((concern, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-yellow-600 mr-2">⚠</span>
                          <span className="text-yellow-700">{concern}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Matched Lenders */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Matched Lenders</h3>
                  <div className="space-y-4">
                    {results.matched_lenders.map((lender, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-gray-800">{lender.lender_name}</h4>
                            <p className="text-sm text-gray-600">{lender.lender_type}</p>
                            <p className="text-sm text-blue-600 mt-1">Rate: {lender.interest_rate_range}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium text-gray-700">Match Score: {lender.match_score}%</div>
                            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                              lender.pre_approval_likelihood === 'High' ? 'bg-green-100 text-green-800' :
                              lender.pre_approval_likelihood === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {lender.pre_approval_likelihood} Pre-approval
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Next Steps */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Recommended Next Steps</h3>
                  <ol className="space-y-2">
                    {results.next_steps.map((step, index) => (
                      <li key={index} className="flex items-start">
                        <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                          {index + 1}
                        </span>
                        <span className="text-gray-700">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Actions */}
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={resetForm}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    New Application
                  </button>
                  <button
                    onClick={() => window.print()}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Print Results
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-xl shadow-xl overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
              <h1 className="text-3xl font-bold">QuickFlow Capital</h1>
              <p className="text-blue-100 mt-2">AI-Powered Business Loan Prequalification</p>
            </div>

            {/* Form */}
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Business Information */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Business Information</h2>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Business Name</label>
                      <input
                        type="text"
                        name="business_name"
                        value={formData.business_name}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter your business name"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
                      <select
                        name="industry"
                        value={formData.industry}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select industry</option>
                        {industries.map(industry => (
                          <option key={industry} value={industry}>{industry}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Years in Business</label>
                      <input
                        type="number"
                        name="years_in_business"
                        value={formData.years_in_business}
                        onChange={handleInputChange}
                        required
                        min="0"
                        max="100"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 5"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Annual Revenue</label>
                      <input
                        type="number"
                        name="annual_revenue"
                        value={formData.annual_revenue}
                        onChange={handleInputChange}
                        required
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 500000"
                      />
                    </div>
                  </div>
                </div>

                {/* Financial Information */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Financial Information</h2>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Credit Score</label>
                      <input
                        type="number"
                        name="credit_score"
                        value={formData.credit_score}
                        onChange={handleInputChange}
                        required
                        min="300"
                        max="850"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 720"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Cash Flow</label>
                      <input
                        type="number"
                        name="monthly_cash_flow"
                        value={formData.monthly_cash_flow}
                        onChange={handleInputChange}
                        required
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 25000"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Existing Debt</label>
                      <input
                        type="number"
                        name="existing_debt"
                        value={formData.existing_debt}
                        onChange={handleInputChange}
                        required
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 50000"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Requested Loan Amount</label>
                      <input
                        type="number"
                        name="loan_amount_requested"
                        value={formData.loan_amount_requested}
                        onChange={handleInputChange}
                        required
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., 100000"
                      />
                    </div>
                  </div>
                </div>

                {/* Loan Details */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Loan Details</h2>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Loan Purpose</label>
                    <select
                      name="loan_purpose"
                      value={formData.loan_purpose}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select loan purpose</option>
                      {loanPurposes.map(purpose => (
                        <option key={purpose} value={purpose}>{purpose}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="bg-gray-50 rounded-lg p-6">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">Contact Information</h2>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <input
                        type="email"
                        name="contact_email"
                        value={formData.contact_email}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="john@business.com"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                      <input
                        type="tel"
                        name="contact_phone"
                        value={formData.contact_phone}
                        onChange={handleInputChange}
                        required
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="(555) 123-4567"
                      />
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">{error}</p>
                  </div>
                )}

                {/* Submit Button */}
                <div className="flex justify-center">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <div className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Analyzing Application...
                      </div>
                    ) : (
                      'Get Prequalification Results'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;