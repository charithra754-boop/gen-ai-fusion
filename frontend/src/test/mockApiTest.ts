/**
 * Test script for Mock API System functionality
 * Verifies query categorization and color-coded responses
 */

import { processMockQuery, categorizeQuery, determineStatus } from '../lib/mockApiSystem';

// Test queries for each category
const testQueries = {
  PIN: [
    "Someone asked for my PIN number",
    "Should I share my OTP?",
    "Bank manager wants my CVV",
    "ಯಾರೋ ನನ್ನ ಪಿನ್ ಸಂಖ್ಯೆ ಕೇಳಿದರು",
    "किसी ने मेरा पिन नंबर मांगा"
  ],
  KCC: [
    "How to apply for KCC loan?",
    "Kisan Credit Card interest rate",
    "My KCC application was rejected",
    "ಕೆಸಿಸಿ ಸಾಲಕ್ಕೆ ಹೇಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸುವುದು?",
    "केसीसी लोन के लिए कैसे आवेदन करें?"
  ],
  STRESS: [
    "My crops are turning yellow",
    "Pest attack on my field",
    "Crop failure due to drought",
    "ನನ್ನ ಬೆಳೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ",
    "मेरी फसलें पीली हो रही हैं"
  ],
  SELL: [
    "When should I sell my wheat?",
    "Current market prices",
    "Best time to harvest",
    "ನನ್ನ ಗೋಧಿಯನ್ನು ಯಾವಾಗ ಮಾರಬೇಕು?",
    "मुझे अपना गेहूं कब बेचना चाहिए?"
  ],
  GENERAL: [
    "What is the weather forecast?",
    "Help me with farming",
    "KisaanMitra information",
    "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಏನು?",
    "मौसम का पूर्वानुमान क्या है?"
  ]
};

// Expected color mappings
const expectedColors = {
  PIN: 'red',      // Security alerts should be red
  KCC: 'green',    // Loan information should be green
  STRESS: 'orange', // Crop stress should be orange/warning
  SELL: 'green',   // Market info should be green
  GENERAL: 'green' // General queries should be green
};

function runMockApiTests() {
  console.log('🧪 Running Mock API System Tests...\n');
  
  let totalTests = 0;
  let passedTests = 0;
  
  // Test each category
  Object.entries(testQueries).forEach(([category, queries]) => {
    console.log(`\n📋 Testing ${category} Category:`);
    console.log('=' .repeat(40));
    
    queries.forEach((query, index) => {
      totalTests++;
      
      // Test categorization
      const detectedCategory = categorizeQuery(query, 'en');
      const categoryMatch = detectedCategory === category;
      
      // Test response generation
      const response = processMockQuery(query, 'en');
      const colorMatch = response.statusColor === expectedColors[category as keyof typeof expectedColors] || 
                        (category === 'STRESS' && response.statusColor === 'red') || // Stress can be red for severe cases
                        (category === 'PIN' && response.statusColor === 'orange'); // PIN can be orange for warnings
      
      // Test multilingual support
      const responseKn = processMockQuery(query, 'kn');
      const responseHi = processMockQuery(query, 'hi');
      const multilingualSupport = responseKn.responseKannada && responseHi.responseHindi;
      
      const testPassed = categoryMatch && colorMatch && multilingualSupport;
      if (testPassed) passedTests++;
      
      console.log(`${index + 1}. Query: "${query}"`);
      console.log(`   Category: ${detectedCategory} ${categoryMatch ? '✅' : '❌'}`);
      console.log(`   Color: ${response.statusColor} ${colorMatch ? '✅' : '❌'}`);
      console.log(`   Confidence: ${response.confidence}%`);
      console.log(`   Agent: ${response.metadata?.agentType}`);
      console.log(`   Multilingual: ${multilingualSupport ? '✅' : '❌'}`);
      console.log(`   Status: ${testPassed ? '✅ PASS' : '❌ FAIL'}\n`);
    });
  });
  
  // Test color-coded status system
  console.log('\n🎨 Testing Color-Coded Status System:');
  console.log('=' .repeat(40));
  
  const colorTests = [
    { query: "CRITICAL: Share PIN immediately", expectedColor: 'red' },
    { query: "KCC approved successfully", expectedColor: 'green' },
    { query: "Crop showing stress symptoms", expectedColor: 'orange' },
    { query: "Market prices are good", expectedColor: 'green' }
  ];
  
  colorTests.forEach((test, index) => {
    totalTests++;
    const response = processMockQuery(test.query, 'en');
    const colorMatch = response.statusColor === test.expectedColor;
    if (colorMatch) passedTests++;
    
    console.log(`${index + 1}. "${test.query}"`);
    console.log(`   Expected: ${test.expectedColor}, Got: ${response.statusColor} ${colorMatch ? '✅' : '❌'}`);
  });
  
  // Summary
  console.log('\n📊 Test Summary:');
  console.log('=' .repeat(40));
  console.log(`Total Tests: ${totalTests}`);
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${totalTests - passedTests}`);
  console.log(`Success Rate: ${Math.round((passedTests / totalTests) * 100)}%`);
  
  if (passedTests === totalTests) {
    console.log('\n🎉 All tests passed! Mock API system is working correctly.');
  } else {
    console.log('\n⚠️  Some tests failed. Check the implementation.');
  }
  
  return { totalTests, passedTests, successRate: (passedTests / totalTests) * 100 };
}

// Export for use in other files
export { runMockApiTests };

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  runMockApiTests();
}