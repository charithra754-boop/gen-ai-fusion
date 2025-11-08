/**
 * Comprehensive Error Handling Test Suite
 * Tests all error scenarios and fallback systems
 */

import { processMockQuery, validateQuery, createFallbackResponse, QueryError } from '../lib/mockApiSystem';

interface TestResult {
  testName: string;
  passed: boolean;
  message: string;
  response?: any;
}

/**
 * Test suite for error handling functionality
 */
export function runErrorHandlingTests(): TestResult[] {
  const results: TestResult[] = [];

  // Test 1: Empty query validation
  console.log('🧪 Running Error Handling Test Suite...\n');

  try {
    const emptyQueryError = validateQuery('');
    results.push({
      testName: 'Empty Query Validation',
      passed: emptyQueryError !== null && emptyQueryError.type === 'validation',
      message: emptyQueryError ? `✅ Correctly detected: ${emptyQueryError.message}` : '❌ Failed to detect empty query',
      response: emptyQueryError
    });
  } catch (error) {
    results.push({
      testName: 'Empty Query Validation',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 2: Long query validation
  try {
    const longQuery = 'a'.repeat(501);
    const longQueryError = validateQuery(longQuery);
    results.push({
      testName: 'Long Query Validation',
      passed: longQueryError !== null && longQueryError.type === 'validation',
      message: longQueryError ? `✅ Correctly detected: ${longQueryError.message}` : '❌ Failed to detect long query',
      response: longQueryError
    });
  } catch (error) {
    results.push({
      testName: 'Long Query Validation',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 3: Malicious content validation
  try {
    const maliciousQuery = '<script>alert("test")</script>';
    const maliciousError = validateQuery(maliciousQuery);
    results.push({
      testName: 'Malicious Content Validation',
      passed: maliciousError !== null && maliciousError.type === 'validation',
      message: maliciousError ? `✅ Correctly detected: ${maliciousError.message}` : '❌ Failed to detect malicious content',
      response: maliciousError
    });
  } catch (error) {
    results.push({
      testName: 'Malicious Content Validation',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 4: Valid query passes validation
  try {
    const validError = validateQuery('How to apply for KCC loan?');
    results.push({
      testName: 'Valid Query Validation',
      passed: validError === null,
      message: validError ? `❌ Valid query rejected: ${validError.message}` : '✅ Valid query accepted',
      response: validError
    });
  } catch (error) {
    results.push({
      testName: 'Valid Query Validation',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 5: Fallback response creation
  try {
    const testError: QueryError = {
      type: 'timeout',
      message: 'Request timed out',
      retryable: true
    };
    const fallbackResponse = createFallbackResponse('test query', testError, 'en');
    results.push({
      testName: 'Fallback Response Creation',
      passed: fallbackResponse.status === 'error' && fallbackResponse.metadata?.errorType === 'timeout',
      message: fallbackResponse.status === 'error' ? '✅ Fallback response created correctly' : '❌ Fallback response incorrect',
      response: fallbackResponse
    });
  } catch (error) {
    results.push({
      testName: 'Fallback Response Creation',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 6: Unrecognized query handling
  try {
    const unrecognizedResponse = processMockQuery('xyz random nonsense query', 'en');
    results.push({
      testName: 'Unrecognized Query Handling',
      passed: unrecognizedResponse.category === 'GENERAL' && (unrecognizedResponse.confidence < 50 || unrecognizedResponse.status === 'error'),
      message: unrecognizedResponse.status === 'error' || unrecognizedResponse.confidence < 50 ? 
        '✅ Unrecognized query handled with fallback' : 
        '❌ Unrecognized query not properly handled',
      response: unrecognizedResponse
    });
  } catch (error) {
    results.push({
      testName: 'Unrecognized Query Handling',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 7: Multilingual fallback responses
  try {
    const kannadaFallback = createFallbackResponse('test', undefined, 'kn');
    const hindiFallback = createFallbackResponse('test', undefined, 'hi');
    results.push({
      testName: 'Multilingual Fallback Responses',
      passed: kannadaFallback.responseKannada.length > 0 && hindiFallback.responseHindi.length > 0,
      message: (kannadaFallback.responseKannada.length > 0 && hindiFallback.responseHindi.length > 0) ? 
        '✅ Multilingual fallback responses generated' : 
        '❌ Multilingual fallback responses missing',
      response: { kannada: kannadaFallback.responseKannada, hindi: hindiFallback.responseHindi }
    });
  } catch (error) {
    results.push({
      testName: 'Multilingual Fallback Responses',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 8: Error response metadata
  try {
    const errorResponse = processMockQuery('', 'en'); // This should trigger validation error
    results.push({
      testName: 'Error Response Metadata',
      passed: errorResponse.metadata?.actionRequired === true && 
              errorResponse.metadata?.retryable !== undefined &&
              errorResponse.metadata?.errorType !== undefined,
      message: (errorResponse.metadata?.actionRequired && errorResponse.metadata?.retryable !== undefined) ? 
        '✅ Error response contains proper metadata' : 
        '❌ Error response missing metadata',
      response: errorResponse.metadata
    });
  } catch (error) {
    results.push({
      testName: 'Error Response Metadata',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 9: System error simulation
  try {
    // Run multiple queries to potentially trigger simulated system error
    let systemErrorTriggered = false;
    for (let i = 0; i < 50; i++) {
      const response = processMockQuery('test query', 'en');
      if (response.metadata?.errorType === 'system') {
        systemErrorTriggered = true;
        break;
      }
    }
    results.push({
      testName: 'System Error Simulation',
      passed: systemErrorTriggered,
      message: systemErrorTriggered ? 
        '✅ System error simulation working (5% chance triggered)' : 
        '⚠️ System error simulation not triggered in 50 attempts (expected due to 5% chance)',
      response: null
    });
  } catch (error) {
    results.push({
      testName: 'System Error Simulation',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  // Test 10: Agricultural query categories still work
  try {
    const pinResponse = processMockQuery('Someone asked for my PIN number', 'en');
    const kccResponse = processMockQuery('How to apply for KCC loan?', 'en');
    const stressResponse = processMockQuery('My crops are dying', 'en');
    const sellResponse = processMockQuery('When to sell wheat?', 'en');
    
    const categoriesCorrect = pinResponse.category === 'PIN' && 
                             kccResponse.category === 'KCC' && 
                             stressResponse.category === 'STRESS' && 
                             sellResponse.category === 'SELL';
    
    results.push({
      testName: 'Agricultural Query Categories',
      passed: categoriesCorrect,
      message: categoriesCorrect ? 
        '✅ All agricultural query categories working correctly' : 
        '❌ Some agricultural query categories not working',
      response: {
        pin: pinResponse.category,
        kcc: kccResponse.category,
        stress: stressResponse.category,
        sell: sellResponse.category
      }
    });
  } catch (error) {
    results.push({
      testName: 'Agricultural Query Categories',
      passed: false,
      message: `❌ Test threw error: ${error.message}`
    });
  }

  return results;
}

/**
 * Display test results in a formatted way
 */
export function displayTestResults(results: TestResult[]): void {
  console.log('\n📊 ERROR HANDLING TEST RESULTS\n');
  console.log('='.repeat(50));
  
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  
  results.forEach((result, index) => {
    console.log(`${index + 1}. ${result.testName}`);
    console.log(`   ${result.message}`);
    if (result.response && typeof result.response === 'object') {
      console.log(`   Response: ${JSON.stringify(result.response, null, 2).substring(0, 100)}...`);
    }
    console.log('');
  });
  
  console.log('='.repeat(50));
  console.log(`📈 SUMMARY: ${passed}/${total} tests passed (${Math.round(passed/total*100)}%)`);
  
  if (passed === total) {
    console.log('🎉 All error handling tests passed! System is robust.');
  } else {
    console.log('⚠️ Some tests failed. Review error handling implementation.');
  }
}

/**
 * Run all tests and display results
 */
export function runCompleteErrorHandlingTest(): void {
  const results = runErrorHandlingTests();
  displayTestResults(results);
}