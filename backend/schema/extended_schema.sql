-- KisaanMitra Extended Database Schema
-- Multi-Agent System Support
-- Adds tables for all 7 agents: CMGA, CRA, GAA, FIA, MIA, LIA, HIA

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- AGENT REGISTRY
-- ============================================
CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_type VARCHAR(50) UNIQUE NOT NULL,
  version VARCHAR(20) NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  capabilities JSONB,
  health_check_url VARCHAR(255),
  last_heartbeat TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- ============================================
-- FPO (Farmer Producer Organizations) - CMGA
-- ============================================
CREATE TABLE IF NOT EXISTS fpos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  registration_number VARCHAR(100) UNIQUE,
  village VARCHAR(100),
  district VARCHAR(100),
  state VARCHAR(100),
  location GEOGRAPHY(POINT, 4326),
  total_members INTEGER DEFAULT 0,
  total_land_area DECIMAL(10, 2), -- in hectares
  formation_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  contact_person VARCHAR(255),
  contact_phone VARCHAR(20),
  contact_email VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fpos_location ON fpos USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_fpos_district ON fpos(district);
CREATE INDEX IF NOT EXISTS idx_fpos_status ON fpos(status);

-- ============================================
-- FPO MEMBERSHIP - CMGA
-- ============================================
CREATE TABLE IF NOT EXISTS fpo_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  join_date DATE NOT NULL,
  land_area DECIMAL(10, 2), -- in hectares
  role VARCHAR(50) DEFAULT 'member', -- member, secretary, president
  investment_units DECIMAL(15, 2) DEFAULT 0,
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(fpo_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_fpo_members_fpo ON fpo_members(fpo_id);
CREATE INDEX IF NOT EXISTS idx_fpo_members_user ON fpo_members(user_id);

-- ============================================
-- INVESTMENT UNITS LEDGER - CMGA
-- ============================================
CREATE TABLE IF NOT EXISTS investment_units (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  member_id UUID REFERENCES fpo_members(id) ON DELETE CASCADE,
  units DECIMAL(15, 2) NOT NULL,
  calculation_basis JSONB, -- land_area, inputs, labor, etc.
  season VARCHAR(50),
  crop_cycle VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  verified_at TIMESTAMPTZ,
  verified_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_investment_units_fpo ON investment_units(fpo_id);
CREATE INDEX IF NOT EXISTS idx_investment_units_member ON investment_units(member_id);
CREATE INDEX IF NOT EXISTS idx_investment_units_season ON investment_units(season);

-- ============================================
-- COLLECTIVE PORTFOLIOS - CMGA
-- ============================================
CREATE TABLE IF NOT EXISTS collective_portfolios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  season VARCHAR(50) NOT NULL,
  year INTEGER NOT NULL,
  planned_crops JSONB, -- [{crop, area, members[]}]
  risk_score DECIMAL(5, 2),
  expected_revenue DECIMAL(15, 2),
  diversification_index DECIMAL(5, 2),
  sharpe_ratio DECIMAL(5, 2),
  status VARCHAR(20) DEFAULT 'planning', -- planning, approved, active, completed
  created_by UUID REFERENCES users(id),
  approved_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolios_fpo ON collective_portfolios(fpo_id);
CREATE INDEX IF NOT EXISTS idx_portfolios_season ON collective_portfolios(season, year);

-- ============================================
-- PROFIT DISTRIBUTIONS - CMGA
-- ============================================
CREATE TABLE IF NOT EXISTS profit_distributions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id) ON DELETE CASCADE,
  portfolio_id UUID REFERENCES collective_portfolios(id),
  member_id UUID REFERENCES fpo_members(id) ON DELETE CASCADE,
  investment_units DECIMAL(15, 2),
  share_percentage DECIMAL(5, 2),
  gross_profit DECIMAL(15, 2),
  deductions DECIMAL(15, 2) DEFAULT 0,
  net_profit DECIMAL(15, 2),
  payment_status VARCHAR(20) DEFAULT 'pending',
  payment_date DATE,
  payment_reference VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_profit_dist_fpo ON profit_distributions(fpo_id);
CREATE INDEX IF NOT EXISTS idx_profit_dist_member ON profit_distributions(member_id);
CREATE INDEX IF NOT EXISTS idx_profit_dist_status ON profit_distributions(payment_status);

-- ============================================
-- MANDI PRICES - MIA
-- ============================================
CREATE TABLE IF NOT EXISTS mandi_prices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  mandi_name VARCHAR(255) NOT NULL,
  state VARCHAR(100),
  district VARCHAR(100),
  commodity VARCHAR(255) NOT NULL,
  variety VARCHAR(255),
  grade VARCHAR(50),
  min_price DECIMAL(10, 2),
  max_price DECIMAL(10, 2),
  modal_price DECIMAL(10, 2),
  arrival_quantity DECIMAL(10, 2), -- in quintals
  unit VARCHAR(20) DEFAULT 'quintal',
  price_date DATE NOT NULL,
  source VARCHAR(100), -- agmarknet, state portal
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mandi_prices_commodity ON mandi_prices(commodity);
CREATE INDEX IF NOT EXISTS idx_mandi_prices_date ON mandi_prices(price_date DESC);
CREATE INDEX IF NOT EXISTS idx_mandi_prices_location ON mandi_prices(state, district);

-- ============================================
-- PRICE FORECASTS - MIA
-- ============================================
CREATE TABLE IF NOT EXISTS price_forecasts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  commodity VARCHAR(255) NOT NULL,
  mandi_name VARCHAR(255),
  forecast_date DATE NOT NULL,
  predicted_price DECIMAL(10, 2),
  lower_bound DECIMAL(10, 2),
  upper_bound DECIMAL(10, 2),
  model_version VARCHAR(50),
  confidence_score DECIMAL(5, 2),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(commodity, mandi_name, forecast_date)
);

CREATE INDEX IF NOT EXISTS idx_price_forecasts_commodity ON price_forecasts(commodity);
CREATE INDEX IF NOT EXISTS idx_price_forecasts_date ON price_forecasts(forecast_date);

-- ============================================
-- IOT SENSORS - CRA
-- ============================================
CREATE TABLE IF NOT EXISTS iot_sensors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sensor_id VARCHAR(100) UNIQUE NOT NULL,
  sensor_type VARCHAR(50), -- soil_moisture, weather_station, water_flow
  location GEOGRAPHY(POINT, 4326),
  farm_id UUID, -- If linked to specific farm
  fpo_id UUID REFERENCES fpos(id),
  farmer_id UUID REFERENCES users(id),
  installation_date DATE,
  status VARCHAR(20) DEFAULT 'active',
  calibration_date DATE,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_iot_sensors_type ON iot_sensors(sensor_type);
CREATE INDEX IF NOT EXISTS idx_iot_sensors_location ON iot_sensors USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_iot_sensors_farmer ON iot_sensors(farmer_id);

-- ============================================
-- IRRIGATION SCHEDULES - CRA
-- ============================================
CREATE TABLE IF NOT EXISTS irrigation_schedules (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID, -- Link to farm/field
  farmer_id UUID REFERENCES users(id),
  fpo_id UUID REFERENCES fpos(id),
  crop_type VARCHAR(100),
  scheduled_time TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER,
  water_volume DECIMAL(10, 2), -- in liters
  status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, executed, skipped, failed
  execution_time TIMESTAMPTZ,
  actual_volume DECIMAL(10, 2),
  created_by VARCHAR(50) DEFAULT 'CRA', -- Agent that created it
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_irrigation_schedules_time ON irrigation_schedules(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_irrigation_schedules_farmer ON irrigation_schedules(farmer_id);
CREATE INDEX IF NOT EXISTS idx_irrigation_schedules_status ON irrigation_schedules(status);

-- ============================================
-- WATER BUDGETS - CRA
-- ============================================
CREATE TABLE IF NOT EXISTS water_budgets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id),
  farmer_id UUID REFERENCES users(id),
  season VARCHAR(50),
  total_allocation DECIMAL(12, 2), -- in cubic meters
  used DECIMAL(12, 2) DEFAULT 0,
  remaining DECIMAL(12, 2),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_water_budgets_farmer ON water_budgets(farmer_id);
CREATE INDEX IF NOT EXISTS idx_water_budgets_fpo ON water_budgets(fpo_id);

-- ============================================
-- SATELLITE IMAGERY METADATA - GAA
-- ============================================
CREATE TABLE IF NOT EXISTS satellite_imagery (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  image_id VARCHAR(255) UNIQUE NOT NULL,
  satellite_source VARCHAR(50), -- sentinel-2, landsat-8
  acquisition_date DATE NOT NULL,
  cloud_coverage DECIMAL(5, 2),
  bounds GEOGRAPHY(POLYGON, 4326),
  resolution_meters DECIMAL(5, 2),
  bands JSONB, -- Available spectral bands
  s3_bucket VARCHAR(255),
  s3_key VARCHAR(500),
  processing_status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_satellite_imagery_date ON satellite_imagery(acquisition_date DESC);
CREATE INDEX IF NOT EXISTS idx_satellite_imagery_bounds ON satellite_imagery USING GIST(bounds);

-- ============================================
-- NDVI ANALYSIS - GAA
-- ============================================
CREATE TABLE IF NOT EXISTS ndvi_analysis (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID,
  farmer_id UUID REFERENCES users(id),
  image_id UUID REFERENCES satellite_imagery(id),
  analysis_date DATE NOT NULL,
  mean_ndvi DECIMAL(5, 4),
  min_ndvi DECIMAL(5, 4),
  max_ndvi DECIMAL(5, 4),
  vegetation_health VARCHAR(20), -- excellent, good, fair, poor, critical
  stress_detected BOOLEAN DEFAULT false,
  stress_areas JSONB, -- GeoJSON of stressed areas
  recommendations TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ndvi_analysis_farmer ON ndvi_analysis(farmer_id);
CREATE INDEX IF NOT EXISTS idx_ndvi_analysis_date ON ndvi_analysis(analysis_date DESC);

-- ============================================
-- YIELD FORECASTS - GAA
-- ============================================
CREATE TABLE IF NOT EXISTS yield_forecasts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID,
  farmer_id UUID REFERENCES users(id),
  fpo_id UUID REFERENCES fpos(id),
  crop_type VARCHAR(100) NOT NULL,
  season VARCHAR(50),
  forecast_date DATE NOT NULL,
  harvest_date DATE,
  predicted_yield DECIMAL(10, 2), -- in quintals
  confidence_score DECIMAL(5, 2),
  model_version VARCHAR(50),
  input_features JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_yield_forecasts_farmer ON yield_forecasts(farmer_id);
CREATE INDEX IF NOT EXISTS idx_yield_forecasts_crop ON yield_forecasts(crop_type);
CREATE INDEX IF NOT EXISTS idx_yield_forecasts_date ON yield_forecasts(forecast_date DESC);

-- ============================================
-- DISEASE & PEST DETECTIONS - GAA
-- ============================================
CREATE TABLE IF NOT EXISTS disease_detections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farm_id UUID,
  farmer_id UUID REFERENCES users(id),
  detection_date TIMESTAMPTZ NOT NULL,
  crop_type VARCHAR(100),
  disease_type VARCHAR(255),
  pest_type VARCHAR(255),
  severity VARCHAR(20), -- low, medium, high, critical
  confidence_score DECIMAL(5, 2),
  image_url VARCHAR(500),
  location GEOGRAPHY(POINT, 4326),
  recommendations TEXT,
  status VARCHAR(20) DEFAULT 'active', -- active, treated, resolved
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_disease_detections_farmer ON disease_detections(farmer_id);
CREATE INDEX IF NOT EXISTS idx_disease_detections_date ON disease_detections(detection_date DESC);
CREATE INDEX IF NOT EXISTS idx_disease_detections_status ON disease_detections(status);

-- ============================================
-- CREDIT SCORES - FIA
-- ============================================
CREATE TABLE IF NOT EXISTS credit_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id) ON DELETE CASCADE,
  score DECIMAL(5, 2) NOT NULL CHECK (score >= 0 AND score <= 1000),
  rating VARCHAR(10), -- AAA, AA, A, BBB, BB, B, C
  calculation_date DATE NOT NULL,
  factors JSONB, -- {yield_history: 0.3, soil_quality: 0.2, ...}
  model_version VARCHAR(50),
  expires_at DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_scores_farmer ON credit_scores(farmer_id);
CREATE INDEX IF NOT EXISTS idx_credit_scores_date ON credit_scores(calculation_date DESC);

-- ============================================
-- LOAN APPLICATIONS - FIA
-- ============================================
CREATE TABLE IF NOT EXISTS loan_applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id) ON DELETE CASCADE,
  credit_score_id UUID REFERENCES credit_scores(id),
  amount DECIMAL(15, 2) NOT NULL,
  purpose TEXT,
  tenure_months INTEGER,
  interest_rate DECIMAL(5, 2),
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, disbursed
  application_date DATE NOT NULL,
  decision_date DATE,
  disbursement_date DATE,
  lender_name VARCHAR(255),
  lender_reference VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_loan_applications_farmer ON loan_applications(farmer_id);
CREATE INDEX IF NOT EXISTS idx_loan_applications_status ON loan_applications(status);

-- ============================================
-- INSURANCE POLICIES - FIA
-- ============================================
CREATE TABLE IF NOT EXISTS insurance_policies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  farmer_id UUID REFERENCES users(id) ON DELETE CASCADE,
  policy_number VARCHAR(100) UNIQUE NOT NULL,
  insurance_type VARCHAR(50), -- crop, weather, livestock
  crop_type VARCHAR(100),
  insured_area DECIMAL(10, 2),
  sum_insured DECIMAL(15, 2),
  premium_amount DECIMAL(15, 2),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  provider_name VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_insurance_policies_farmer ON insurance_policies(farmer_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON insurance_policies(status);

-- ============================================
-- INSURANCE CLAIMS - FIA
-- ============================================
CREATE TABLE IF NOT EXISTS insurance_claims (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  policy_id UUID REFERENCES insurance_policies(id) ON DELETE CASCADE,
  farmer_id UUID REFERENCES users(id),
  claim_number VARCHAR(100) UNIQUE NOT NULL,
  loss_type VARCHAR(100), -- drought, flood, pest, disease
  loss_date DATE NOT NULL,
  reported_date DATE NOT NULL,
  estimated_loss DECIMAL(15, 2),
  assessed_loss DECIMAL(15, 2),
  claim_amount DECIMAL(15, 2),
  status VARCHAR(20) DEFAULT 'submitted', -- submitted, under_review, approved, rejected, paid
  satellite_evidence UUID REFERENCES satellite_imagery(id),
  adjuster_notes TEXT,
  settlement_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_insurance_claims_policy ON insurance_claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_insurance_claims_farmer ON insurance_claims(farmer_id);
CREATE INDEX IF NOT EXISTS idx_insurance_claims_status ON insurance_claims(status);

-- ============================================
-- COLD STORAGE FACILITIES - LIA
-- ============================================
CREATE TABLE IF NOT EXISTS cold_storage_facilities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  location GEOGRAPHY(POINT, 4326),
  address TEXT,
  district VARCHAR(100),
  state VARCHAR(100),
  total_capacity DECIMAL(10, 2), -- in metric tons
  available_capacity DECIMAL(10, 2),
  temperature_range VARCHAR(50), -- e.g., "0-4°C"
  commodities_supported JSONB, -- ["potato", "onion", "tomato"]
  power_source VARCHAR(50), -- grid, solar, hybrid
  rental_rate_per_quintal DECIMAL(10, 2),
  contact_person VARCHAR(255),
  contact_phone VARCHAR(20),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cold_storage_location ON cold_storage_facilities USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_cold_storage_district ON cold_storage_facilities(district);

-- ============================================
-- POST HARVEST LOSSES - LIA
-- ============================================
CREATE TABLE IF NOT EXISTS post_harvest_losses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  fpo_id UUID REFERENCES fpos(id),
  farmer_id UUID REFERENCES users(id),
  commodity VARCHAR(255) NOT NULL,
  total_harvest DECIMAL(10, 2), -- in quintals
  loss_quantity DECIMAL(10, 2),
  loss_percentage DECIMAL(5, 2),
  loss_stage VARCHAR(50), -- harvesting, transport, storage
  loss_reason VARCHAR(100), -- temperature, moisture, pest, damage
  loss_date DATE,
  estimated_value_loss DECIMAL(15, 2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_losses_commodity ON post_harvest_losses(commodity);
CREATE INDEX IF NOT EXISTS idx_losses_date ON post_harvest_losses(loss_date DESC);

-- ============================================
-- MESSAGE TEMPLATES (for SMS/IVR) - HIA
-- ============================================
CREATE TABLE IF NOT EXISTS message_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  template_key VARCHAR(100) UNIQUE NOT NULL,
  category VARCHAR(50), -- alert, advisory, notification
  channel VARCHAR(20), -- sms, ivr, whatsapp
  language VARCHAR(10),
  template_text TEXT NOT NULL,
  variables JSONB, -- Placeholder variables
  priority VARCHAR(20) DEFAULT 'normal',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_message_templates_key ON message_templates(template_key);
CREATE INDEX IF NOT EXISTS idx_message_templates_category ON message_templates(category);

-- ============================================
-- SENT MESSAGES LOG - HIA
-- ============================================
CREATE TABLE IF NOT EXISTS sent_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  recipient_id UUID REFERENCES users(id),
  channel VARCHAR(20), -- sms, ivr, whatsapp, push
  template_id UUID REFERENCES message_templates(id),
  message_content TEXT,
  phone_number VARCHAR(20),
  status VARCHAR(20) DEFAULT 'sent', -- sent, delivered, failed, read
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  delivered_at TIMESTAMPTZ,
  cost DECIMAL(10, 4),
  provider_reference VARCHAR(255),
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_sent_messages_recipient ON sent_messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_sent_messages_status ON sent_messages(status);
CREATE INDEX IF NOT EXISTS idx_sent_messages_sent_at ON sent_messages(sent_at DESC);
