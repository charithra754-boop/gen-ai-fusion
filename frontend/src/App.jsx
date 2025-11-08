
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Send, History, RefreshCw, Wheat, AlertTriangle, CheckCircle, XCircle, Shield, TrendingUp, Sprout, CreditCard, HelpCircle, Trash2, Play, BookOpen, Target, Award } from 'lucide-react';
import { processMockQuery } from './lib/mockApiSystem';

const App = () => {
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showTutorial, setShowTutorial] = useState(false);
  const [tutorialStep, setTutorialStep] = useState(0);
  const [tutorialCompleted, setTutorialCompleted] = useState(false);

  // Load query history and tutorial state from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('kisaanmitra-query-history');
    const savedTutorialCompleted = localStorage.getItem('kisaanmitra-tutorial-completed');
    
    if (savedHistory) {
      try {
        setQueryHistory(JSON.parse(savedHistory));
      } catch (error) {
        console.error('Error loading query history:', error);
      }
    }
    
    if (savedTutorialCompleted === 'true') {
      setTutorialCompleted(true);
    } else {
      // Show tutorial for new users
      setShowTutorial(true);
    }
  }, []);

  // Save query history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('kisaanmitra-query-history', JSON.stringify(queryHistory));
  }, [queryHistory]);

  // Tutorial steps configuration
  const tutorialSteps = [
    {
      id: 0,
      title: "Welcome to KisaanMitra!",
      description: "Your AI-powered agricultural advisory system with 7 specialized agents",
      action: "Get Started",
      query: null,
      expectedCategory: null,
      icon: "🌾"
    },
    {
      id: 1,
      title: "Security Alert System",
      description: "Test our fraud detection system by asking about PIN sharing",
      action: "Try Security Query",
      query: "Someone asked for my PIN number",
      expectedCategory: "PIN",
      icon: "🔒"
    },
    {
      id: 2,
      title: "Financial Services",
      description: "Learn about KCC loans and financial assistance",
      action: "Ask About KCC",
      query: "How to apply for KCC loan?",
      expectedCategory: "KCC",
      icon: "💳"
    },
    {
      id: 3,
      title: "Crop Health Monitoring",
      description: "Get expert advice on crop diseases and stress",
      action: "Check Crop Health",
      query: "My crops are turning yellow",
      expectedCategory: "STRESS",
      icon: "🌱"
    },
    {
      id: 4,
      title: "Market Intelligence",
      description: "Optimize your selling decisions with market data",
      action: "Get Market Advice",
      query: "When should I sell my wheat?",
      expectedCategory: "SELL",
      icon: "💰"
    },
    {
      id: 5,
      title: "Tutorial Complete!",
      description: "You've successfully tested all major features. Continue exploring!",
      action: "Finish Tutorial",
      query: null,
      expectedCategory: null,
      icon: "🎉"
    }
  ];

  // Sample queries for demonstration
  const sampleQueries = [
    "Someone asked for my PIN number",
    "How to apply for KCC loan?", 
    "My crops are turning yellow",
    "When should I sell my wheat?",
    "What is the weather forecast?"
  ];

  // Tutorial functions
  const startTutorial = () => {
    setShowTutorial(true);
    setTutorialStep(0);
    setTutorialCompleted(false);
  };

  const nextTutorialStep = () => {
    if (tutorialStep < tutorialSteps.length - 1) {
      setTutorialStep(tutorialStep + 1);
    } else {
      completeTutorial();
    }
  };

  const completeTutorial = () => {
    setShowTutorial(false);
    setTutorialCompleted(true);
    localStorage.setItem('kisaanmitra-tutorial-completed', 'true');
  };

  const runTutorialQuery = (step) => {
    if (step.query) {
      setQuery(step.query);
      processQuery(step.query, true);
    } else {
      nextTutorialStep();
    }
  };

  const processQuery = async (inputQuery, fromTutorial = false) => {
    if (!inputQuery.trim()) return;
    
    setIsProcessing(true);
    
    // Add to query history
    const historyEntry = {
      id: Date.now(),
      query: inputQuery,
      timestamp: new Date().toISOString()
    };
    setQueryHistory(prev => [historyEntry, ...prev.slice(0, 9)]); // Keep last 10 queries
    
    try {
      // Simulate API processing delay with timeout
      const processingPromise = new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 10000)
      );
      
      await Promise.race([processingPromise, timeoutPromise]);
      
      // Process the query with error handling
      const response = processMockQuery(inputQuery, 'en');
      
      // Add retry functionality for failed requests
      if (response.status === 'error' && response.metadata?.retryable) {
        response.metadata.retryAction = () => processQuery(inputQuery, fromTutorial);
      }
      
      setResponses(prev => [response, ...prev]);
      setQuery('');

      // Handle tutorial progression
      if (fromTutorial && showTutorial) {
        const currentStep = tutorialSteps[tutorialStep];
        if (currentStep.expectedCategory && response.category === currentStep.expectedCategory) {
          setTimeout(() => {
            nextTutorialStep();
          }, 2000);
        }
      }
    } catch (error) {
      console.error('Query processing error:', error);
      
      // Create error response based on error type
      let errorResponse;
      if (error.message === 'Request timeout') {
        errorResponse = {
          id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          category: 'GENERAL',
          status: 'error',
          statusColor: 'red',
          confidence: 0,
          response: '⏱️ Request timed out. Please try again with a shorter question or check your connection.',
          responseKannada: '⏱️ ವಿನಂತಿ ಸಮಯ ಮೀರಿದೆ. ದಯವಿಟ್ಟು ಚಿಕ್ಕ ಪ್ರಶ್ನೆಯೊಂದಿಗೆ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ನಿಮ್ಮ ಸಂಪರ್ಕವನ್ನು ಪರಿಶೀಲಿಸಿ.',
          responseHindi: '⏱️ अनुरोध का समय समाप्त हो गया। कृपया छोटे प्रश्न के साथ पुनः प्रयास करें या अपना कनेक्शन जांचें।',
          icon: '⏱️',
          timestamp: new Date().toISOString(),
          metadata: {
            agentType: 'Error Handler',
            actionRequired: true,
            urgency: 'medium',
            errorType: 'timeout',
            retryable: true,
            retryAction: () => processQuery(inputQuery, fromTutorial)
          }
        };
      } else {
        errorResponse = {
          id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          category: 'GENERAL',
          status: 'error',
          statusColor: 'red',
          confidence: 0,
          response: '🚨 System error occurred. Please try again or contact support if the problem persists. Emergency agricultural helpline: 1551',
          responseKannada: '🚨 ಸಿಸ್ಟಮ್ ದೋಷ ಸಂಭವಿಸಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ ಅಥವಾ ಸಮಸ್ಯೆ ಮುಂದುವರಿದರೆ ಬೆಂಬಲವನ್ನು ಸಂಪರ್ಕಿಸಿ. ತುರ್ತು ಕೃಷಿ ಸಹಾಯವಾಣಿ: 1551',
          responseHindi: '🚨 सिस्टम त्रुटि हुई। कृपया पुनः प्रयास करें या यदि समस्या बनी रहे तो सहायता से संपर्क करें। आपातकालीन कृषि हेल्पलाइन: 1551',
          icon: '🚨',
          timestamp: new Date().toISOString(),
          metadata: {
            agentType: 'Error Handler',
            actionRequired: true,
            urgency: 'high',
            errorType: 'system',
            retryable: true,
            retryAction: () => processQuery(inputQuery, fromTutorial)
          }
        };
      }
      
      setResponses(prev => [errorResponse, ...prev]);
      setQuery('');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    processQuery(query);
  };

  const handleSampleQuery = (sampleQuery) => {
    setQuery(sampleQuery);
    processQuery(sampleQuery);
  };

  const clearHistory = () => {
    setResponses([]);
    setQueryHistory([]);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-orange-600" />;
      case 'error':
        return <XCircle className="w-6 h-6 text-red-600" />;
      default:
        return <HelpCircle className="w-6 h-6 text-gray-600" />;
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'PIN':
        return <Shield className="w-5 h-5" />;
      case 'KCC':
        return <CreditCard className="w-5 h-5" />;
      case 'STRESS':
        return <Sprout className="w-5 h-5" />;
      case 'SELL':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <HelpCircle className="w-5 h-5" />;
    }
  };

  const getBackgroundColor = (statusColor) => {
    switch (statusColor) {
      case 'green':
        return 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200';
      case 'orange':
        return 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200';
      case 'red':
        return 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200';
      default:
        return 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-200';
    }
  };

  // Tutorial Modal Component
  const TutorialModal = () => {
    if (!showTutorial) return null;

    const currentStep = tutorialSteps[tutorialStep];

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <Card className="max-w-md w-full bg-white p-6 relative">
          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Tutorial Progress</span>
              <span>{tutorialStep + 1} / {tutorialSteps.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((tutorialStep + 1) / tutorialSteps.length) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Step Content */}
          <div className="text-center space-y-4">
            <div className="text-6xl">{currentStep.icon}</div>
            <h2 className="text-2xl font-bold text-gray-800">{currentStep.title}</h2>
            <p className="text-gray-600">{currentStep.description}</p>

            {/* Action Buttons */}
            <div className="flex space-x-3 justify-center">
              {tutorialStep > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setTutorialStep(tutorialStep - 1)}
                  className="px-6"
                >
                  Previous
                </Button>
              )}
              
              <Button
                onClick={() => runTutorialQuery(currentStep)}
                className="bg-green-600 hover:bg-green-700 px-6"
              >
                {currentStep.action}
              </Button>

              {tutorialStep === 0 && (
                <Button
                  variant="outline"
                  onClick={completeTutorial}
                  className="px-6"
                >
                  Skip Tutorial
                </Button>
              )}
            </div>

            {/* Tutorial Query Preview */}
            {currentStep.query && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Query to test:</p>
                <p className="font-mono text-sm bg-white p-2 rounded border">
                  "{currentStep.query}"
                </p>
              </div>
            )}
          </div>

          {/* Close button */}
          <button
            onClick={completeTutorial}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </Card>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 mb-6">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Wheat className="text-green-600" size={36} />
            <div>
              <h1 className="text-2xl font-bold text-green-800">KisaanMitra</h1>
              <p className="text-sm text-gray-600">Agricultural Advisory System</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Badge variant="outline" className="bg-green-100 text-green-700 border-green-300">
              AI-Powered Advisory
            </Badge>
            <Button
              onClick={startTutorial}
              variant="outline"
              size="sm"
              className="bg-blue-100 text-blue-700 border-blue-300 hover:bg-blue-200"
            >
              <BookOpen className="w-4 h-4 mr-2" />
              {tutorialCompleted ? 'Restart Tutorial' : 'Start Tutorial'}
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 space-y-6 max-w-4xl">
        {/* Main Query Interface */}
        <Card className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <div className="text-center space-y-4 mb-6">
            <h2 className="text-2xl font-bold text-blue-800">Agricultural Query System</h2>
            <p className="text-blue-600">
              Ask about crops, loans, market prices, or security with color-coded status indicators
            </p>
          </div>

          {/* Query Input Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about crops, loans, market prices, or security..."
                className="flex-1 text-base"
                disabled={isProcessing}
              />
              <Button 
                type="submit" 
                disabled={isProcessing || !query.trim()}
                className="bg-green-600 hover:bg-green-700 px-6"
              >
                {isProcessing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                <span className="ml-2 hidden sm:inline">Submit</span>
              </Button>
            </div>

            {/* Sample Queries */}
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Sample Queries:</p>
              <div className="flex flex-wrap gap-2">
                {sampleQueries.map((sample, index) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors text-xs sm:text-sm"
                    onClick={() => handleSampleQuery(sample)}
                  >
                    {sample}
                  </Badge>
                ))}
              </div>
            </div>
          </form>
        </Card>

        {/* Status Summary Dashboard */}
        {responses.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="p-4 bg-green-50 border-green-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {responses.filter(r => r.statusColor === 'green').length}
                </div>
                <div className="text-sm text-green-700">Success</div>
              </div>
            </Card>
            <Card className="p-4 bg-orange-50 border-orange-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {responses.filter(r => r.statusColor === 'orange').length}
                </div>
                <div className="text-sm text-orange-700">Warning</div>
              </div>
            </Card>
            <Card className="p-4 bg-red-50 border-red-200">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {responses.filter(r => r.statusColor === 'red').length}
                </div>
                <div className="text-sm text-red-700">Alert</div>
              </div>
            </Card>
          </div>
        )}

        {/* Response History */}
        {responses.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
                <History className="w-5 h-5" />
                <span>Response History</span>
              </h3>
              <Button
                onClick={clearHistory}
                variant="outline"
                size="sm"
                className="text-gray-600 hover:text-gray-800"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Clear
              </Button>
            </div>

            {/* Response List */}
            <div className="space-y-4">
              {responses.map((response) => (
                <Card key={response.id} className={`p-4 ${getBackgroundColor(response.statusColor)} transition-all duration-300 hover:shadow-lg`}>
                  {/* Header with Status and Category */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 space-y-2 sm:space-y-0">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(response.status)}
                      <Badge 
                        variant="outline" 
                        className={`
                          ${response.statusColor === 'green' ? 'border-green-300 text-green-700 bg-green-100' : ''}
                          ${response.statusColor === 'orange' ? 'border-orange-300 text-orange-700 bg-orange-100' : ''}
                          ${response.statusColor === 'red' ? 'border-red-300 text-red-700 bg-red-100' : ''}
                        `}
                      >
                        {response.status.charAt(0).toUpperCase() + response.status.slice(1)}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      {getCategoryIcon(response.category)}
                      <span>{response.category}</span>
                    </div>
                  </div>

                  {/* Response Content */}
                  <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                      <span className="text-2xl flex-shrink-0">{response.icon}</span>
                      <div className="flex-1">
                        <p className={`
                          font-medium leading-relaxed
                          ${response.statusColor === 'green' ? 'text-green-800' : ''}
                          ${response.statusColor === 'orange' ? 'text-orange-800' : ''}
                          ${response.statusColor === 'red' ? 'text-red-800' : ''}
                        `}>
                          {response.response}
                        </p>
                      </div>
                    </div>

                    {/* Error Actions */}
                    {response.status === 'error' && response.metadata?.retryable && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                          <Button
                            onClick={() => response.metadata?.retryAction?.()}
                            variant="outline"
                            size="sm"
                            className="bg-blue-50 text-blue-700 border-blue-300 hover:bg-blue-100"
                            disabled={isProcessing}
                          >
                            <RefreshCw className={`w-4 h-4 mr-2 ${isProcessing ? 'animate-spin' : ''}`} />
                            Try Again
                          </Button>
                          
                          {response.metadata?.errorType === 'timeout' && (
                            <span className="text-xs text-gray-600">
                              💡 Tip: Try a shorter, more specific question
                            </span>
                          )}
                          
                          {response.metadata?.errorType === 'validation' && (
                            <span className="text-xs text-gray-600">
                              💡 Tip: Ask about crops, loans, market prices, or security
                            </span>
                          )}
                          
                          {response.metadata?.errorType === 'system' && (
                            <span className="text-xs text-gray-600">
                              💡 Emergency helpline: 1551 (Agricultural support)
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-200 space-y-1 sm:space-y-0">
                      <div className="flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-4">
                        <span>Agent: {response.metadata?.agentType}</span>
                        <span>Confidence: {response.confidence}%</span>
                        <span>{new Date(response.timestamp).toLocaleString()}</span>
                        {response.metadata?.errorType && (
                          <span className="text-red-600">Error: {response.metadata.errorType}</span>
                        )}
                      </div>
                      
                      {response.metadata?.actionRequired && (
                        <Badge 
                          variant="outline" 
                          className={`
                            text-xs
                            ${response.metadata.urgency === 'high' ? 'border-red-300 text-red-600 bg-red-50' : ''}
                            ${response.metadata.urgency === 'medium' ? 'border-orange-300 text-orange-600 bg-orange-50' : ''}
                            ${response.metadata.urgency === 'low' ? 'border-blue-300 text-blue-600 bg-blue-50' : ''}
                          `}
                        >
                          Action Required
                        </Badge>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Query History Sidebar */}
        {queryHistory.length > 0 && (
          <Card className="p-4 bg-gray-50 border-gray-200">
            <h4 className="text-md font-semibold text-gray-700 mb-3">Recent Queries</h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {queryHistory.slice(0, 5).map((historyItem) => (
                <div 
                  key={historyItem.id}
                  className="text-sm text-gray-600 p-2 bg-white rounded border cursor-pointer hover:bg-blue-50 transition-colors"
                  onClick={() => setQuery(historyItem.query)}
                >
                  <div className="truncate">{historyItem.query}</div>
                  <div className="text-xs text-gray-400">
                    {new Date(historyItem.timestamp).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Welcome Message */}
        {responses.length === 0 && (
          <Card className="p-6 text-center bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
            <Wheat className="mx-auto text-green-600 mb-4" size={48} />
            <h3 className="text-xl font-semibold text-gray-800 mb-2">Welcome to KisaanMitra</h3>
            <p className="text-gray-600 mb-4">
              Your AI-powered agricultural advisory system with 7 specialized agents. Ask questions about crops, loans, market prices, or security concerns.
            </p>
            
            {tutorialCompleted && (
              <div className="mb-4 p-3 bg-green-100 border border-green-300 rounded-lg">
                <div className="flex items-center justify-center space-x-2 text-green-700">
                  <Award className="w-5 h-5" />
                  <span className="font-medium">Tutorial Completed!</span>
                </div>
                <p className="text-sm text-green-600 mt-1">
                  You've successfully learned all major features. Continue exploring!
                </p>
              </div>
            )}

            <div className="space-y-3">
              <p className="text-sm text-gray-500">
                Responses are color-coded: <span className="text-green-600 font-medium">Green (Success)</span>, 
                <span className="text-orange-600 font-medium"> Orange (Warning)</span>, 
                <span className="text-red-600 font-medium"> Red (Alert)</span>
              </p>
              
              {!tutorialCompleted && (
                <div className="flex items-center justify-center space-x-2 text-blue-600">
                  <Target className="w-4 h-4" />
                  <span className="text-sm">Click "Start Tutorial" above to learn the system!</span>
                </div>
              )}
            </div>

            {/* Feature Showcase */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-white rounded-lg border border-green-200 hover:shadow-md transition-shadow">
                <div className="text-center">
                  <Shield className="w-8 h-8 text-red-500 mx-auto mb-2" />
                  <h4 className="font-semibold text-sm text-gray-800">Security</h4>
                  <p className="text-xs text-gray-600">Fraud Detection</p>
                </div>
              </div>
              <div className="p-4 bg-white rounded-lg border border-green-200 hover:shadow-md transition-shadow">
                <div className="text-center">
                  <CreditCard className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                  <h4 className="font-semibold text-sm text-gray-800">Finance</h4>
                  <p className="text-xs text-gray-600">KCC Loans</p>
                </div>
              </div>
              <div className="p-4 bg-white rounded-lg border border-green-200 hover:shadow-md transition-shadow">
                <div className="text-center">
                  <Sprout className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <h4 className="font-semibold text-sm text-gray-800">Crops</h4>
                  <p className="text-xs text-gray-600">Health Monitoring</p>
                </div>
              </div>
              <div className="p-4 bg-white rounded-lg border border-green-200 hover:shadow-md transition-shadow">
                <div className="text-center">
                  <TrendingUp className="w-8 h-8 text-purple-500 mx-auto mb-2" />
                  <h4 className="font-semibold text-sm text-gray-800">Market</h4>
                  <p className="text-xs text-gray-600">Price Intelligence</p>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Tutorial Modal */}
      <TutorialModal />
    </div>
  );
};
=======
import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [chatHistory, setChatHistory] = useState([
    {
      sender: 'agent',
      text: '🌾 Namaste! I am KisaanMitra, your AI farming assistant. Ask me about loans, insurance, crop health, irrigation, or market prices!',
      timestamp: Date.now()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userQuery = inputText.trim();
    setInputText(''); // Clear input immediately
    
    const API_URL = 'http://127.0.0.1:8000/v1/agent/master/';
    
    // Add user message to chat immediately
    setChatHistory(prev => [...prev, { 
      sender: 'user', 
      text: userQuery, 
      timestamp: Date.now() 
    }]);

    setIsLoading(true);
    
    try {
      // Prepare the request (Input Contract)
      const payload = JSON.stringify({
        contents: [{
          parts: [{
            text: userQuery
          }]
        }]
      });
      
      // Call the API
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: payload
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      
      // Parse response (Output Contract)
      const result = await response.json();
      const agentText = result.candidates[0].content.parts[0].text;
      
      // Add agent response to chat
      setChatHistory(prev => [...prev, { 
        sender: 'agent', 
        text: agentText, 
        timestamp: Date.now() 
      }]);
      
    } catch (error) {
      console.error('KisaanMitra API Error:', error);
      setChatHistory(prev => [...prev, { 
        sender: 'agent', 
        text: '❌ Connection error. Please check if the server is running on http://127.0.0.1:8000', 
        timestamp: Date.now() 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    "What is the KCC interest rate?",
    "Tell me about PM-KISAN scheme",
    "I received an SMS asking for my OTP",
    "Schedule irrigation for my plot"
  ];

  const handleQuickQuestion = (question) => {
    setInputText(question);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌾 KisaanMitra</h1>
        <p>Your AI-Powered Farming Assistant</p>
      </header>

      <div className="chat-container">
        <div className="chat-messages">
          {chatHistory.map((msg, index) => (
            <div 
              key={index} 
              className={`message ${msg.sender === 'user' ? 'user-message' : 'agent-message'}`}
            >
              <div className="message-bubble">
                <div className="message-text">{msg.text}</div>
                <div className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message agent-message">
              <div className="message-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={chatEndRef} />
        </div>

        {chatHistory.length <= 1 && (
          <div className="quick-questions">
            <p>Quick questions to try:</p>
            <div className="quick-buttons">
              {quickQuestions.map((q, i) => (
                <button 
                  key={i}
                  onClick={() => handleQuickQuestion(q)}
                  className="quick-button"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="chat-input-container">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about loans, schemes, crop health, irrigation..."
            className="chat-input"
            rows="2"
            disabled={isLoading}
          />
          <button 
            onClick={handleSendMessage}
            className="send-button"
            disabled={isLoading || !inputText.trim()}
          >
            {isLoading ? '⏳' : '📤 Send'}
          </button>
        </div>
      </div>

      <footer className="app-footer">
        <p>Powered by Gemini AI • Made for Indian Farmers</p>
      </footer>
    </div>
  );
}
09d0cb0b (Fixes)

export default App;