import React, { useState, useReducer, useEffect, useRef, useCallback } from 'react';

// API Configuration
const apiEndpoint = "http://127.0.0.1:8000/v1/agent/master/";

// Agent Configuration with enhanced details
const AGENTS = {
  CMGA: { 
    name: 'Collective Market Governance', 
    color: '#2D5016', 
    icon: '🏛️', 
    status: 'active',
    description: 'Portfolio planning, Investment Units, Profit distribution',
    capabilities: ['FPO Management', 'Investment Tracking', 'Profit Distribution', 'Portfolio Optimization'],
    responseTime: '245ms',
    accuracy: '94%'
  },
  MIA: { 
    name: 'Market Intelligence', 
    color: '#17A2B8', 
    icon: '📊', 
    status: 'active',
    description: 'Mandi prices, Demand forecasting, Price predictions',
    capabilities: ['Price Forecasting', 'Market Analysis', 'Demand Prediction', 'Trade Optimization'],
    responseTime: '180ms',
    accuracy: '91%'
  },
  GAA: { 
    name: 'Geo-Agronomy', 
    color: '#28A745', 
    icon: '🌱', 
    status: 'active',
    description: 'Satellite imagery, NDVI, Disease detection, Yield forecasting',
    capabilities: ['Crop Monitoring', 'Disease Detection', 'Yield Prediction', 'Soil Analysis'],
    responseTime: '320ms',
    accuracy: '89%'
  },
  CRA: { 
    name: 'Climate & Resource', 
    color: '#FFC107', 
    icon: '🌤️', 
    status: 'active',
    description: 'IoT sensors, Autonomous irrigation, Water budgets',
    capabilities: ['Weather Monitoring', 'Irrigation Control', 'Resource Management', 'Climate Adaptation'],
    responseTime: '210ms',
    accuracy: '92%'
  },
  FIA: { 
    name: 'Financial Inclusion', 
    color: '#DC3545', 
    icon: '💳', 
    status: 'active',
    description: 'Credit scoring, Insurance automation, Anti-fraud',
    capabilities: ['Credit Assessment', 'Insurance Processing', 'Fraud Detection', 'Financial Planning'],
    responseTime: '155ms',
    accuracy: '96%'
  },
  LIA: { 
    name: 'Logistics Infrastructure', 
    color: '#6F42C1', 
    icon: '🚛', 
    status: 'active',
    description: 'Cold chain, Route optimization, Loss tracking',
    capabilities: ['Supply Chain', 'Route Planning', 'Storage Management', 'Loss Prevention'],
    responseTime: '275ms',
    accuracy: '88%'
  },
  HIA: { 
    name: 'Human Interface', 
    color: '#FD7E14', 
    icon: '🗣️', 
    status: 'active',
    description: 'Multilingual, Voice, SMS/IVR, Agent synthesis',
    capabilities: ['Voice Processing', 'Language Translation', 'Communication Hub', 'User Interface'],
    responseTime: '95ms',
    accuracy: '97%'
  }
};

// Feature Categories
const FEATURE_CATEGORIES = {
  CURRENT: {
    name: 'Current Features (8% Complete)',
    color: '#28A745',
    features: [
      'Multilingual voice interface (EN, KN, HI)',
      'Soil analysis with crop recommendations',
      'Weather display and farming tips',
      'MCP infrastructure (Redis + RabbitMQ)',
      'Agent base architecture',
      'Extended database schema (30+ tables)',
      'Docker development environment'
    ]
  },
  INPROGRESS: {
    name: 'In Development (Next 3 Months)',
    color: '#FFC107',
    features: [
      'CMGA (Collective Market Governance)',
      'MIA (Market Intelligence with mandi prices)',
      'FPO Dashboard UI',
      'Investment Unit Calculator',
      'Profit Distribution Engine',
      'Portfolio Optimization Algorithm'
    ]
  },
  PLANNED: {
    name: 'Planned Features (6-18 Months)',
    color: '#17A2B8',
    features: [
      'Sentinel-2 satellite imagery integration',
      'NDVI analysis pipeline',
      'Disease detection CNN (75%+ accuracy)',
      'IoT sensor integration',
      'Autonomous irrigation control',
      'AI credit scoring system',
      'Banking API integration',
      'Cold storage capacity planning',
      'Route optimization algorithms'
    ]
  }
};

// Color Palette
const COLORS = {
  forestGreen: '#2D5016',
  dangerRed: '#DC3545',
  lightGray: '#F8F9FA',
  charcoal: '#2C3E50',
  skyBlue: '#17A2B8',
  warmOrange: '#FD7E14',
  goldenYellow: '#FFC107',
  success: '#28A745',
  warning: '#FFC107',
  info: '#17A2B8'
};

// Enhanced State Management
const initialState = {
  chatHistory: [],
  isLoading: false,
  activeAgents: Object.keys(AGENTS),
  selectedAgent: null,
  draggedAgent: null,
  currentView: 'dashboard', // dashboard, user, admin, analytics, settings, help
  showOnboarding: false,
  showTutorial: false,
  notifications: [],
  searchQuery: '',
  filters: {
    agent: 'all',
    timeRange: '24h',
    status: 'all'
  },
  userProfile: {
    name: 'Farmer User',
    location: 'Karnataka, India',
    farmSize: '2.5 acres',
    crops: ['Tomato', 'Onion', 'Rice'],
    fpoMember: true
  },
  serverStats: {
    totalServers: 7,
    activeServers: 7,
    responseTime: '245ms',
    uptime: '99.8%',
    totalQueries: 1247,
    successRate: '94.2%',
    avgResponseTime: '215ms'
  },
  analytics: {
    dailyQueries: [45, 52, 38, 61, 47, 55, 42],
    agentUsage: {
      MIA: 28,
      GAA: 22,
      FIA: 18,
      CRA: 15,
      CMGA: 10,
      LIA: 4,
      HIA: 3
    },
    successRates: {
      MIA: 96,
      GAA: 89,
      FIA: 94,
      CRA: 91,
      CMGA: 87,
      LIA: 93,
      HIA: 98
    }
  }
};

function dashboardReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'ADD_MESSAGE':
      return { 
        ...state, 
        chatHistory: [action.payload, ...state.chatHistory.slice(0, 49)] // Keep last 50 messages
      };
    case 'SELECT_AGENT':
      return { ...state, selectedAgent: action.payload };
    case 'SET_DRAGGED_AGENT':
      return { ...state, draggedAgent: action.payload };
    case 'SET_VIEW':
      return { ...state, currentView: action.payload };
    case 'UPDATE_SERVER_STATS':
      return { ...state, serverStats: { ...state.serverStats, ...action.payload } };
    case 'CLEAR_CHAT':
      return { ...state, chatHistory: [] };
    case 'ADD_NOTIFICATION':
      return { 
        ...state, 
        notifications: [action.payload, ...state.notifications.slice(0, 9)] 
      };
    case 'REMOVE_NOTIFICATION':
      return { 
        ...state, 
        notifications: state.notifications.filter(n => n.id !== action.payload) 
      };
    case 'SET_SEARCH_QUERY':
      return { ...state, searchQuery: action.payload };
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.payload } };
    case 'TOGGLE_ONBOARDING':
      return { ...state, showOnboarding: !state.showOnboarding };
    case 'TOGGLE_TUTORIAL':
      return { ...state, showTutorial: !state.showTutorial };
    case 'UPDATE_USER_PROFILE':
      return { ...state, userProfile: { ...state.userProfile, ...action.payload } };
    default:
      return state;
  }
}

// Main Dashboard Component
const KisaanMitraDashboard = () => {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('EN');
  const [query, setQuery] = useState('');
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [state.chatHistory, scrollToBottom]);

  // Enhanced effects and utilities
  useEffect(() => {
    // Simulate server stats updates
    const interval = setInterval(() => {
      dispatch({
        type: 'UPDATE_SERVER_STATS',
        payload: {
          responseTime: `${Math.floor(Math.random() * 300 + 200)}ms`,
          activeServers: Math.floor(Math.random() * 2) + 6,
          totalQueries: state.serverStats.totalQueries + Math.floor(Math.random() * 3),
          successRate: `${(94 + Math.random() * 4).toFixed(1)}%`
        }
      });
    }, 5000);
    return () => clearInterval(interval);
  }, [state.serverStats.totalQueries]);

  // Load user preferences
  useEffect(() => {
    const savedTheme = localStorage.getItem('kisaan-theme');
    const savedLanguage = localStorage.getItem('kisaan-language');
    const savedProfile = localStorage.getItem('kisaan-profile');
    
    if (savedTheme) setDarkMode(savedTheme === 'dark');
    if (savedLanguage) setLanguage(savedLanguage);
    if (savedProfile) {
      dispatch({ type: 'UPDATE_USER_PROFILE', payload: JSON.parse(savedProfile) });
    }
  }, []);

  // Save preferences
  useEffect(() => {
    localStorage.setItem('kisaan-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('kisaan-language', language);
    localStorage.setItem('kisaan-profile', JSON.stringify(state.userProfile));
  }, [darkMode, language, state.userProfile]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'k':
            e.preventDefault();
            inputRef.current?.focus();
            break;
          case '/':
            e.preventDefault();
            dispatch({ type: 'SET_VIEW', payload: 'help' });
            break;
          case 'd':
            e.preventDefault();
            setDarkMode(!darkMode);
            break;
        }
      }
    };
    
    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [darkMode]);

  // Notification system
  const addNotification = useCallback((message, type = 'info', duration = 5000) => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toISOString()
    };
    
    dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
    
    if (duration > 0) {
      setTimeout(() => {
        dispatch({ type: 'REMOVE_NOTIFICATION', payload: notification.id });
      }, duration);
    }
  }, []);

  // Enhanced search functionality
  const handleSearch = useCallback((searchTerm) => {
    dispatch({ type: 'SET_SEARCH_QUERY', payload: searchTerm });
    
    if (searchTerm.trim()) {
      const filteredHistory = state.chatHistory.filter(msg => 
        msg.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        msg.agent?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      if (filteredHistory.length === 0) {
        addNotification(`No results found for "${searchTerm}"`, 'warning');
      }
    }
  }, [state.chatHistory, addNotification]);

  // Voice input simulation
  const handleVoiceInput = useCallback(() => {
    addNotification('Voice input activated. Speak now...', 'info');
    
    // Simulate voice recognition
    setTimeout(() => {
      const voiceQueries = [
        'What is the weather forecast for tomorrow?',
        'Check my crop health status',
        'Show me current market prices',
        'Help with KCC loan application'
      ];
      
      const randomQuery = voiceQueries[Math.floor(Math.random() * voiceQueries.length)];
      setQuery(randomQuery);
      addNotification('Voice input recognized', 'success');
    }, 2000);
  }, [addNotification]);

  // Export chat history
  const exportChatHistory = useCallback(() => {
    const dataStr = JSON.stringify(state.chatHistory, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `kisaan-chat-history-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    addNotification('Chat history exported successfully', 'success');
  }, [state.chatHistory, addNotification]);

  // Send Message Function
  const sendMessage = async (message, targetAgent = null) => {
    if (!message.trim()) return;

    dispatch({ type: 'SET_LOADING', payload: true });

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      agent: targetAgent
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

      // Mock response based on query content
      let response = generateMockResponse(message, targetAgent);
      
      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: response.content,
        timestamp: new Date().toISOString(),
        agent: targetAgent || response.agent,
        status: response.status,
        confidence: response.confidence
      };

      dispatch({ type: 'ADD_MESSAGE', payload: agentMessage });
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Failed to get response from agent. Please try again.',
        timestamp: new Date().toISOString(),
        agent: targetAgent || 'SYSTEM'
      };
      dispatch({ type: 'ADD_MESSAGE', payload: errorMessage });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Generate Mock Response
  const generateMockResponse = (query, agent) => {
    const queryLower = query.toLowerCase();
    
    // Fraud detection
    if (queryLower.includes('pin') || queryLower.includes('password') || queryLower.includes('otp')) {
      return {
        content: '🚨 CRITICAL WARNING: Never share your PIN, OTP, or passwords with anyone. This appears to be a potential fraud attempt. Contact your bank immediately if someone is asking for this information.',
        agent: 'FIA',
        status: 'danger',
        confidence: 95
      };
    }

    // Agent-specific responses
    if (agent) {
      switch (agent) {
        case 'CMGA':
          return {
            content: `🏛️ CMGA Analysis: Based on collective market data, I recommend coordinating with your FPO for better bargaining power. Current portfolio optimization suggests diversifying into high-value crops.`,
            agent: 'CMGA',
            status: 'success',
            confidence: 88
          };
        case 'MIA':
          return {
            content: `📊 Market Intelligence: Current mandi prices show upward trend. Tomato: ₹2,400/quintal (+15%), Onion: ₹1,800/quintal (+8%). Optimal selling window in next 3-5 days.`,
            agent: 'MIA',
            status: 'success',
            confidence: 92
          };
        case 'GAA':
          return {
            content: `🌱 Geo-Agronomy Report: NDVI analysis shows healthy crop growth. Satellite imagery indicates optimal vegetation index. Continue current irrigation schedule.`,
            agent: 'GAA',
            status: 'success',
            confidence: 85
          };
        case 'CRA':
          return {
            content: `🌤️ Climate Advisory: Weather forecast shows 15mm rainfall expected in next 48 hours. Adjust irrigation schedule accordingly. Soil moisture levels optimal.`,
            agent: 'CRA',
            status: 'warning',
            confidence: 78
          };
        case 'FIA':
          return {
            content: `💳 Financial Advisory: KCC loan eligibility confirmed. Interest rate: 7% (reduced to 4% on timely repayment). Required documents: Land records, Aadhar, PAN.`,
            agent: 'FIA',
            status: 'success',
            confidence: 90
          };
        case 'LIA':
          return {
            content: `🚛 Logistics Update: Cold storage availability: 85%. Optimal transport route identified. Estimated delivery time: 6-8 hours. Cost: ₹450/quintal.`,
            agent: 'LIA',
            status: 'success',
            confidence: 87
          };
        case 'HIA':
          return {
            content: `🗣️ Human Interface: Query processed in ${language}. Voice synthesis ready. SMS notification sent. Multi-channel communication active.`,
            agent: 'HIA',
            status: 'success',
            confidence: 95
          };
      }
    }

    // General query processing
    if (queryLower.includes('crop') || queryLower.includes('disease')) {
      return {
        content: '🌱 Crop health analysis indicates potential stress. Recommend immediate field inspection and soil testing. GAA agent suggests fungicide application.',
        agent: 'GAA',
        status: 'warning',
        confidence: 82
      };
    }

    if (queryLower.includes('price') || queryLower.includes('market')) {
      return {
        content: '📊 Market analysis shows favorable conditions. MIA recommends holding produce for 3-5 days for better prices. Expected price increase: 12-15%.',
        agent: 'MIA',
        status: 'success',
        confidence: 89
      };
    }

    if (queryLower.includes('loan') || queryLower.includes('credit')) {
      return {
        content: '💳 Credit assessment complete. FIA confirms eligibility for KCC loan. Pre-approved amount: ₹2,50,000. Processing time: 7-10 days.',
        agent: 'FIA',
        status: 'success',
        confidence: 91
      };
    }

    return {
      content: '🌾 KisaanMitra Master Agent: Query processed successfully. All 7 specialized agents are operational and ready to assist with your agricultural needs.',
      agent: 'MASTER',
      status: 'success',
      confidence: 85
    };
  };

  // Enhanced Top Navigation Component
  const TopNavigation = () => (
    <div className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800'} shadow-lg border-b-2 border-green-500`}>
      {/* Main Navigation Bar */}
      <div className="px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-2">
            <span className="text-3xl">🌾</span>
            <div>
              <h1 className="text-2xl font-bold text-green-600">KisaanMitra</h1>
              <p className="text-xs opacity-75">Multi-Agent Agricultural Intelligence</p>
            </div>
          </div>
          
          {/* Status Indicators */}
          <div className="hidden lg:flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-green-100 px-3 py-1 rounded-full">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm font-medium text-green-700">{state.serverStats.activeServers}/7 Agents</span>
            </div>
            <div className="flex items-center space-x-2 bg-blue-100 px-3 py-1 rounded-full">
              <span className="text-sm font-medium text-blue-700">⚡ {state.serverStats.responseTime}</span>
            </div>
            <div className="flex items-center space-x-2 bg-purple-100 px-3 py-1 rounded-full">
              <span className="text-sm font-medium text-purple-700">📊 {state.serverStats.successRate}</span>
            </div>
          </div>
        </div>
        
        {/* Right Side Controls */}
        <div className="flex items-center space-x-2">
          {/* Search Bar */}
          <div className="hidden md:flex relative">
            <input
              type="text"
              placeholder="Search conversations... (Ctrl+K)"
              value={state.searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-64 px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <span className="absolute right-3 top-2.5 text-xs text-gray-400">⌘K</span>
          </div>

          {/* Notifications */}
          <div className="relative">
            <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
              🔔
              {state.notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {state.notifications.length}
                </span>
              )}
            </button>
          </div>

          {/* User Profile */}
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold">
              {state.userProfile.name.charAt(0)}
            </div>
            <div className="hidden md:block">
              <div className="text-sm font-medium">{state.userProfile.name}</div>
              <div className="text-xs text-gray-500">{state.userProfile.location}</div>
            </div>
          </div>

          {/* Language Selector */}
          <select 
            value={language} 
            onChange={(e) => setLanguage(e.target.value)}
            className="px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="EN">🇺🇸 EN</option>
            <option value="HI">🇮🇳 हिंदी</option>
            <option value="KN">🇮🇳 ಕನ್ನಡ</option>
          </select>

          {/* Theme Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title="Toggle theme (Ctrl+D)"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            ☰
          </button>
        </div>
      </div>

      {/* Secondary Navigation */}
      <div className="px-4 py-2 border-t border-gray-200 flex items-center justify-between">
        <div className="flex space-x-1">
          {[
            { id: 'dashboard', label: '🏠 Dashboard', icon: '🏠' },
            { id: 'user', label: '👨‍🌾 Chat', icon: '💬' },
            { id: 'admin', label: '⚙️ Agents', icon: '🤖' },
            { id: 'analytics', label: '📊 Analytics', icon: '📈' },
            { id: 'settings', label: '⚙️ Settings', icon: '⚙️' },
            { id: 'help', label: '❓ Help', icon: '❓' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => dispatch({ type: 'SET_VIEW', payload: tab.id })}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                state.currentView === tab.id
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
            >
              <span className="hidden md:inline">{tab.label}</span>
              <span className="md:hidden">{tab.icon}</span>
            </button>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="hidden lg:flex items-center space-x-4 text-sm text-gray-600">
          <span>📈 {state.serverStats.totalQueries} queries today</span>
          <span>⏱️ Avg: {state.serverStats.avgResponseTime}</span>
          <span>✅ {state.serverStats.uptime} uptime</span>
        </div>
      </div>
    </div>
  );

  // Side Navigation Component
  const SideNavigation = () => (
    <div className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-gray-50 text-gray-800'} w-64 h-full border-r border-gray-200 p-4`}>
      <div className="space-y-4">
        <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-4 rounded-lg">
          <h3 className="font-bold text-lg">System Status</h3>
          <div className="mt-2 space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Response Time:</span>
              <span className="font-mono">{state.serverStats.responseTime}</span>
            </div>
            <div className="flex justify-between">
              <span>Uptime:</span>
              <span className="font-mono">{state.serverStats.uptime}</span>
            </div>
            <div className="flex justify-between">
              <span>Active Agents:</span>
              <span className="font-mono">{state.serverStats.activeServers}/7</span>
            </div>
          </div>
        </div>

        {currentView === 'admin' && (
          <div className="space-y-2">
            <h4 className="font-semibold text-gray-600">Agent Management</h4>
            {Object.entries(AGENTS).map(([key, agent]) => (
              <div
                key={key}
                draggable
                onDragStart={() => dispatch({ type: 'SET_DRAGGED_AGENT', payload: key })}
                className={`p-3 rounded-lg border-2 border-dashed border-gray-300 cursor-move hover:border-blue-400 transition-colors ${
                  state.selectedAgent === key ? 'bg-blue-100 border-blue-400' : 'bg-white'
                }`}
                onClick={() => dispatch({ type: 'SELECT_AGENT', payload: key })}
              >
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{agent.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium text-sm">{key}</div>
                    <div className="text-xs text-gray-500">{agent.name}</div>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {currentView === 'user' && (
          <div className="space-y-2">
            <h4 className="font-semibold text-gray-600">Quick Actions</h4>
            <button
              onClick={() => sendMessage("What are the current market prices?")}
              className="w-full p-3 text-left bg-white rounded-lg border hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium text-sm">Market Prices</div>
              <div className="text-xs text-gray-500">Get latest mandi rates</div>
            </button>
            <button
              onClick={() => sendMessage("Check my crop health status")}
              className="w-full p-3 text-left bg-white rounded-lg border hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium text-sm">Crop Health</div>
              <div className="text-xs text-gray-500">NDVI & satellite analysis</div>
            </button>
            <button
              onClick={() => sendMessage("KCC loan application help")}
              className="w-full p-3 text-left bg-white rounded-lg border hover:bg-gray-50 transition-colors"
            >
              <div className="font-medium text-sm">Financial Services</div>
              <div className="text-xs text-gray-500">Loans & insurance</div>
            </button>
          </div>
        )}
      </div>
    </div>
  );

  // Chat Interface Component
  const ChatInterface = () => (
    <div className="flex-1 flex flex-col">
      {/* Chat Header */}
      <div className={`${darkMode ? 'bg-gray-700 text-white' : 'bg-white text-gray-800'} p-4 border-b border-gray-200 flex justify-between items-center`}>
        <div>
          <h2 className="text-lg font-semibold">
            {currentView === 'admin' ? 'Agent Communication Hub' : 'Agricultural Advisory Chat'}
          </h2>
          <p className="text-sm opacity-75">
            {state.selectedAgent 
              ? `Communicating with ${AGENTS[state.selectedAgent]?.name}` 
              : 'Multi-agent agricultural intelligence system'}
          </p>
        </div>
        <button
          onClick={() => dispatch({ type: 'CLEAR_CHAT' })}
          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm"
        >
          Clear Chat
        </button>
      </div>

      {/* Message Display */}
      <MessageDisplay />

      {/* Enhanced Input Area */}
      <div className={`${darkMode ? 'bg-gray-700' : 'bg-white'} p-4 border-t border-gray-200`}>
        {/* Quick Suggestions */}
        {query === '' && (
          <div className="mb-3">
            <div className="text-xs text-gray-500 mb-2">Quick suggestions:</div>
            <div className="flex flex-wrap gap-2">
              {[
                "Market prices today",
                "Crop health check",
                "Weather forecast",
                "KCC loan help",
                "Irrigation schedule"
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setQuery(suggestion)}
                  className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="mb-2 text-xs text-gray-500 flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
              <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
            </div>
            <span>AI is thinking...</span>
          </div>
        )}

        {/* Main Input Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage(query, state.selectedAgent);
            setQuery('');
          }}
          className="flex space-x-2"
        >
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setIsTyping(e.target.value.length > 0);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Escape') {
                  setQuery('');
                  setIsTyping(false);
                }
              }}
              placeholder={
                state.selectedAgent 
                  ? `Ask ${state.selectedAgent} agent...` 
                  : "Ask about crops, markets, loans, or farming advice..."
              }
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={state.isLoading}
            />
            
            {/* Character Counter */}
            <div className="absolute right-3 top-3 text-xs text-gray-400">
              {query.length}/500
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2">
            {/* Voice Input */}
            <button
              type="button"
              onClick={handleVoiceInput}
              className="px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              title="Voice Input (Ctrl+Shift+V)"
            >
              🎤
            </button>

            {/* Attachment (Future) */}
            <button
              type="button"
              className="px-4 py-3 bg-gray-200 text-gray-600 rounded-lg hover:bg-gray-300 transition-colors"
              title="Attach File (Coming Soon)"
            >
              📎
            </button>

            {/* Send Button */}
            <button
              type="submit"
              disabled={state.isLoading || !query.trim() || query.length > 500}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {state.isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span className="hidden sm:inline">Sending...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <span>Send</span>
                  <span className="text-xs opacity-75">↵</span>
                </div>
              )}
            </button>
          </div>
        </form>

        {/* Input Help Text */}
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Press Enter to send</span>
            <span>Esc to clear</span>
            {state.selectedAgent && (
              <span className="text-green-600">→ Direct to {state.selectedAgent}</span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span>Powered by KisaanMitra AI</span>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    </div>
  );

  // Message Display Component
  const MessageDisplay = () => (
    <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {state.chatHistory.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🌾</div>
          <h3 className="text-xl font-semibold text-gray-600 mb-2">
            Welcome to KisaanMitra
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Your AI-powered agricultural advisory system. Ask questions about crops, markets, 
            financial services, or get expert farming advice from our specialized agents.
          </p>
          {currentView === 'admin' && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg max-w-md mx-auto">
              <p className="text-sm text-blue-700">
                <strong>Admin Mode:</strong> Drag and drop agents from the sidebar to communicate directly with specific agricultural intelligence modules.
              </p>
            </div>
          )}
        </div>
      ) : (
        state.chatHistory.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-green-600 text-white'
                  : message.type === 'error'
                  ? 'bg-red-100 text-red-800 border border-red-200'
                  : message.status === 'danger'
                  ? 'bg-red-50 text-red-800 border-l-4 border-red-500'
                  : message.status === 'warning'
                  ? 'bg-yellow-50 text-yellow-800 border-l-4 border-yellow-500'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              {message.type !== 'user' && (
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-lg">{AGENTS[message.agent]?.icon || '🤖'}</span>
                  <span className="font-semibold text-sm">{message.agent}</span>
                  {message.confidence && (
                    <span className="text-xs opacity-75">({message.confidence}%)</span>
                  )}
                </div>
              )}
              <p className="text-sm leading-relaxed">{message.content}</p>
              <div className="text-xs opacity-75 mt-2">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))
      )}
      
      {state.isLoading && (
        <div className="flex justify-start">
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 max-w-xs">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
              <span className="text-sm text-gray-500">Agent processing...</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Auto-scroll anchor */}
      <div ref={chatEndRef} />
    </div>
  );

  // Admin Dashboard Layout
  const AdminDashboard = () => (
    <div className="flex-1 flex">
      <SideNavigation />
      <div className="flex-1 flex flex-col">
        {/* Agent Grid */}
        <div className="p-6 bg-gray-100 border-b">
          <h3 className="text-lg font-semibold mb-4">Agent Status Grid</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {Object.entries(AGENTS).map(([key, agent]) => (
              <div
                key={key}
                className={`p-4 rounded-lg border-2 text-center cursor-pointer transition-all ${
                  state.selectedAgent === key
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
                onClick={() => dispatch({ type: 'SELECT_AGENT', payload: key })}
              >
                <div className="text-2xl mb-2">{agent.icon}</div>
                <div className="font-medium text-sm">{key}</div>
                <div className={`w-2 h-2 rounded-full mx-auto mt-2 ${
                  agent.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
              </div>
            ))}
          </div>
        </div>
        <ChatInterface />
      </div>
    </div>
  );

  // User Dashboard Layout
  const UserDashboard = () => (
    <div className="flex-1 flex">
      <SideNavigation />
      <ChatInterface />
    </div>
  );

  // Enhanced Dashboard Views
  const DashboardOverview = () => (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Welcome back, {state.userProfile.name}! 🌾</h2>
            <p className="opacity-90">Your agricultural intelligence platform is ready to assist you.</p>
            <div className="mt-4 flex items-center space-x-4 text-sm">
              <span>📍 {state.userProfile.location}</span>
              <span>🌾 {state.userProfile.farmSize}</span>
              <span>🏛️ FPO Member: {state.userProfile.fpoMember ? 'Yes' : 'No'}</span>
            </div>
          </div>
          <div className="text-6xl opacity-20">🚜</div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Agents</p>
              <p className="text-2xl font-bold text-green-600">{state.serverStats.activeServers}/7</p>
            </div>
            <div className="text-3xl">🤖</div>
          </div>
          <div className="mt-2 text-sm text-green-600">All systems operational</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Queries</p>
              <p className="text-2xl font-bold text-blue-600">{state.serverStats.totalQueries}</p>
            </div>
            <div className="text-3xl">💬</div>
          </div>
          <div className="mt-2 text-sm text-blue-600">+12% from yesterday</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-purple-600">{state.serverStats.successRate}</p>
            </div>
            <div className="text-3xl">✅</div>
          </div>
          <div className="mt-2 text-sm text-purple-600">Excellent performance</div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Response</p>
              <p className="text-2xl font-bold text-orange-600">{state.serverStats.avgResponseTime}</p>
            </div>
            <div className="text-3xl">⚡</div>
          </div>
          <div className="mt-2 text-sm text-orange-600">Lightning fast</div>
        </div>
      </div>

      {/* Feature Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Object.entries(FEATURE_CATEGORIES).map(([key, category]) => (
          <div key={key} className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center space-x-2 mb-4">
              <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: category.color }}></div>
              <h3 className="font-semibold text-gray-800">{category.name}</h3>
            </div>
            <ul className="space-y-2">
              {category.features.map((feature, index) => (
                <li key={index} className="flex items-start space-x-2 text-sm">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span className="text-gray-600">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Agent Status Overview */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Agent Performance Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(AGENTS).map(([key, agent]) => (
            <div key={key} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{agent.icon}</span>
                <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>
              <h4 className="font-medium text-sm mb-1">{key}</h4>
              <p className="text-xs text-gray-500 mb-2">{agent.description}</p>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span>Response:</span>
                  <span className="font-mono">{agent.responseTime}</span>
                </div>
                <div className="flex justify-between">
                  <span>Accuracy:</span>
                  <span className="font-mono">{agent.accuracy}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Market Prices', icon: '📊', action: () => sendMessage("What are current market prices?") },
            { label: 'Crop Health', icon: '🌱', action: () => sendMessage("Check my crop health status") },
            { label: 'Weather Forecast', icon: '🌤️', action: () => sendMessage("What's the weather forecast?") },
            { label: 'Financial Help', icon: '💳', action: () => sendMessage("Help with KCC loan application") },
            { label: 'Export Data', icon: '📥', action: exportChatHistory },
            { label: 'Voice Input', icon: '🎤', action: handleVoiceInput },
            { label: 'Tutorial', icon: '🎓', action: () => dispatch({ type: 'TOGGLE_TUTORIAL' }) },
            { label: 'Settings', icon: '⚙️', action: () => dispatch({ type: 'SET_VIEW', payload: 'settings' }) }
          ].map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className="p-4 border rounded-lg hover:bg-gray-50 transition-colors text-center"
            >
              <div className="text-2xl mb-2">{action.icon}</div>
              <div className="text-sm font-medium">{action.label}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  // Analytics Dashboard
  const AnalyticsDashboard = () => (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        <div className="flex space-x-2">
          <select className="px-3 py-2 border rounded-lg text-sm">
            <option>Last 7 days</option>
            <option>Last 30 days</option>
            <option>Last 90 days</option>
          </select>
          <button className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">Export Report</button>
        </div>
      </div>

      {/* Usage Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Daily Query Volume</h3>
          <div className="h-64 flex items-end justify-between space-x-2">
            {state.analytics.dailyQueries.map((queries, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full bg-green-500 rounded-t"
                  style={{ height: `${(queries / Math.max(...state.analytics.dailyQueries)) * 200}px` }}
                ></div>
                <div className="text-xs mt-2 text-gray-600">Day {index + 1}</div>
                <div className="text-xs font-medium">{queries}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Agent Usage Distribution</h3>
          <div className="space-y-3">
            {Object.entries(state.analytics.agentUsage).map(([agent, usage]) => (
              <div key={agent} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span>{AGENTS[agent]?.icon}</span>
                  <span className="text-sm font-medium">{agent}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(usage / Math.max(...Object.values(state.analytics.agentUsage))) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">{usage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Success Rates */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Agent Success Rates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(state.analytics.successRates).map(([agent, rate]) => (
            <div key={agent} className="text-center p-4 border rounded-lg">
              <div className="text-2xl mb-2">{AGENTS[agent]?.icon}</div>
              <div className="font-medium text-sm">{agent}</div>
              <div className="text-2xl font-bold text-green-600 mt-2">{rate}%</div>
              <div className="text-xs text-gray-500">Success Rate</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Settings Dashboard
  const SettingsDashboard = () => (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <h2 className="text-2xl font-bold">Settings</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Profile Settings */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">User Profile</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input 
                type="text" 
                value={state.userProfile.name}
                onChange={(e) => dispatch({ type: 'UPDATE_USER_PROFILE', payload: { name: e.target.value } })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Location</label>
              <input 
                type="text" 
                value={state.userProfile.location}
                onChange={(e) => dispatch({ type: 'UPDATE_USER_PROFILE', payload: { location: e.target.value } })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Farm Size</label>
              <input 
                type="text" 
                value={state.userProfile.farmSize}
                onChange={(e) => dispatch({ type: 'UPDATE_USER_PROFILE', payload: { farmSize: e.target.value } })}
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Primary Crops</label>
              <input 
                type="text" 
                value={state.userProfile.crops.join(', ')}
                onChange={(e) => dispatch({ type: 'UPDATE_USER_PROFILE', payload: { crops: e.target.value.split(', ') } })}
                className="w-full px-3 py-2 border rounded-lg"
                placeholder="Tomato, Onion, Rice"
              />
            </div>
          </div>
        </div>

        {/* System Preferences */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Dark Mode</span>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`w-12 h-6 rounded-full transition-colors ${darkMode ? 'bg-green-600' : 'bg-gray-300'}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-1'}`}></div>
              </button>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Voice Notifications</span>
              <button className="w-12 h-6 bg-green-600 rounded-full">
                <div className="w-5 h-5 bg-white rounded-full translate-x-6"></div>
              </button>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Auto-save Chat</span>
              <button className="w-12 h-6 bg-green-600 rounded-full">
                <div className="w-5 h-5 bg-white rounded-full translate-x-6"></div>
              </button>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Default Language</label>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="EN">English</option>
                <option value="HI">हिंदी (Hindi)</option>
                <option value="KN">ಕನ್ನಡ (Kannada)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Data Management</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={exportChatHistory}
            className="p-4 border rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            <div className="text-2xl mb-2">📥</div>
            <div className="text-sm font-medium">Export Chat History</div>
          </button>
          <button 
            onClick={() => dispatch({ type: 'CLEAR_CHAT' })}
            className="p-4 border border-red-200 rounded-lg hover:bg-red-50 transition-colors text-center text-red-600"
          >
            <div className="text-2xl mb-2">🗑️</div>
            <div className="text-sm font-medium">Clear All Data</div>
          </button>
          <button className="p-4 border rounded-lg hover:bg-gray-50 transition-colors text-center">
            <div className="text-2xl mb-2">🔄</div>
            <div className="text-sm font-medium">Sync Settings</div>
          </button>
        </div>
      </div>
    </div>
  );

  // Help Dashboard
  const HelpDashboard = () => (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <h2 className="text-2xl font-bold">Help & Support</h2>
      
      {/* Quick Help */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-2">Need Help? 🤝</h3>
        <p className="mb-4">Get instant support for your agricultural queries and platform navigation.</p>
        <div className="flex space-x-4">
          <button 
            onClick={() => dispatch({ type: 'TOGGLE_TUTORIAL' })}
            className="px-4 py-2 bg-white text-blue-600 rounded-lg font-medium"
          >
            Start Tutorial
          </button>
          <button className="px-4 py-2 border border-white rounded-lg">
            Contact Support
          </button>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Frequently Asked Questions</h3>
        <div className="space-y-4">
          {[
            {
              q: "How do I communicate with specific agents?",
              a: "Click on any agent in the Agent Control panel or drag them to the chat area to start a direct conversation."
            },
            {
              q: "What types of agricultural queries can I ask?",
              a: "You can ask about crop health, market prices, weather forecasts, financial services, logistics, and general farming advice."
            },
            {
              q: "How accurate are the AI responses?",
              a: "Our agents maintain 85-97% accuracy rates across different domains, with continuous learning and improvement."
            },
            {
              q: "Can I export my conversation history?",
              a: "Yes, use the Export button in Settings or Quick Actions to download your chat history as a JSON file."
            },
            {
              q: "Is my data secure?",
              a: "Absolutely. All communications are encrypted, and we follow strict data privacy protocols for farmer information."
            }
          ].map((faq, index) => (
            <div key={index} className="border-b pb-4">
              <h4 className="font-medium text-gray-800 mb-2">{faq.q}</h4>
              <p className="text-gray-600 text-sm">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="bg-white rounded-lg p-6 shadow-sm border">
        <h3 className="text-lg font-semibold mb-4">Keyboard Shortcuts</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { key: 'Ctrl + K', action: 'Focus search bar' },
            { key: 'Ctrl + D', action: 'Toggle dark mode' },
            { key: 'Ctrl + /', action: 'Open help' },
            { key: 'Enter', action: 'Send message' },
            { key: 'Esc', action: 'Clear input' },
            { key: 'Tab', action: 'Navigate between sections' }
          ].map((shortcut, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium">{shortcut.action}</span>
              <kbd className="px-2 py-1 bg-gray-200 rounded text-xs font-mono">{shortcut.key}</kbd>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Main Dashboard Layout with enhanced routing
  const DashboardLayout = () => (
    <div className={`h-screen flex flex-col ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
      <TopNavigation />
      
      {/* Notifications */}
      {state.notifications.length > 0 && (
        <div className="fixed top-20 right-4 z-50 space-y-2">
          {state.notifications.slice(0, 3).map((notification) => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg shadow-lg max-w-sm ${
                notification.type === 'success' ? 'bg-green-500 text-white' :
                notification.type === 'warning' ? 'bg-yellow-500 text-white' :
                notification.type === 'error' ? 'bg-red-500 text-white' :
                'bg-blue-500 text-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm">{notification.message}</span>
                <button
                  onClick={() => dispatch({ type: 'REMOVE_NOTIFICATION', payload: notification.id })}
                  className="ml-2 text-white hover:text-gray-200"
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Render appropriate view */}
        {state.currentView === 'dashboard' && <DashboardOverview />}
        {state.currentView === 'user' && <UserDashboard />}
        {state.currentView === 'admin' && <AdminDashboard />}
        {state.currentView === 'analytics' && <AnalyticsDashboard />}
        {state.currentView === 'settings' && <SettingsDashboard />}
        {state.currentView === 'help' && <HelpDashboard />}
      </div>

      {/* Tutorial Overlay */}
      {state.showTutorial && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-8 max-w-md mx-4">
            <h3 className="text-xl font-bold mb-4">Welcome to KisaanMitra! 🌾</h3>
            <p className="text-gray-600 mb-6">
              This tutorial will guide you through the key features of your agricultural intelligence platform.
            </p>
            <div className="flex space-x-4">
              <button
                onClick={() => dispatch({ type: 'TOGGLE_TUTORIAL' })}
                className="px-4 py-2 bg-green-600 text-white rounded-lg"
              >
                Start Tutorial
              </button>
              <button
                onClick={() => dispatch({ type: 'TOGGLE_TUTORIAL' })}
                className="px-4 py-2 border rounded-lg"
              >
                Skip
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  return <DashboardLayout />;
};

export default KisaanMitraDashboard;