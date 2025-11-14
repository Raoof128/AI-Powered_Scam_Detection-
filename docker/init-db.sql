-- Initialize scam detection database schema

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create scam_reports table
CREATE TABLE IF NOT EXISTS scam_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    scam_probability DECIMAL(5, 4) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    detected_patterns JSONB,
    metadata JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_scam_reports_created_at ON scam_reports(created_at);
CREATE INDEX idx_scam_reports_risk_level ON scam_reports(risk_level);
CREATE INDEX idx_scam_reports_message_type ON scam_reports(message_type);
CREATE INDEX idx_scam_reports_scam_probability ON scam_reports(scam_probability);

-- Create detection_patterns table
CREATE TABLE IF NOT EXISTS detection_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) UNIQUE NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_regex TEXT,
    weight DECIMAL(3, 2) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default Australian scam patterns
INSERT INTO detection_patterns (pattern_name, pattern_type, description, weight) VALUES
    ('ato_impersonation', 'australian', 'Australian Taxation Office impersonation', 1.0),
    ('mygov_impersonation', 'australian', 'MyGov account scams', 1.0),
    ('centrelink_scam', 'australian', 'Centrelink payment scams', 0.9),
    ('auspost_scam', 'australian', 'Australia Post delivery scams', 0.8),
    ('banking_scam', 'australian', 'Australian bank impersonation', 1.0),
    ('urgent_action', 'behavioral', 'Urgency and pressure tactics', 0.7),
    ('suspicious_url', 'technical', 'Suspicious or shortened URLs', 0.9),
    ('credential_request', 'behavioral', 'Requests for credentials or personal info', 1.0)
ON CONFLICT (pattern_name) DO NOTHING;

-- Create feedback_loop table
CREATE TABLE IF NOT EXISTS feedback_loop (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES scam_reports(id) ON DELETE CASCADE,
    user_feedback VARCHAR(20) NOT NULL,
    corrected_label VARCHAR(20),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for feedback
CREATE INDEX idx_feedback_loop_report_id ON feedback_loop(report_id);
CREATE INDEX idx_feedback_loop_created_at ON feedback_loop(created_at);

-- Create performance_metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    scam_detected INTEGER DEFAULT 0,
    legitimate_detected INTEGER DEFAULT 0,
    avg_processing_time_ms DECIMAL(10, 2),
    p95_processing_time_ms INTEGER,
    p99_processing_time_ms INTEGER,
    accuracy DECIMAL(5, 4),
    precision_score DECIMAL(5, 4),
    recall_score DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    false_positive_rate DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- Create index for performance metrics
CREATE INDEX idx_performance_metrics_date ON performance_metrics(date);

-- Create api_keys table for authentication
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Create index for API keys
CREATE INDEX idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_scam_reports_updated_at
    BEFORE UPDATE ON scam_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_detection_patterns_updated_at
    BEFORE UPDATE ON detection_patterns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scamdetector;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scamdetector;

-- Create view for daily statistics
CREATE OR REPLACE VIEW daily_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_reports,
    COUNT(*) FILTER (WHERE risk_level = 'high') as high_risk,
    COUNT(*) FILTER (WHERE risk_level = 'medium') as medium_risk,
    COUNT(*) FILTER (WHERE risk_level = 'low') as low_risk,
    AVG(scam_probability) as avg_scam_probability,
    AVG(processing_time_ms) as avg_processing_time_ms
FROM scam_reports
GROUP BY DATE(created_at)
ORDER BY date DESC;

COMMENT ON TABLE scam_reports IS 'Stores all scam detection reports with predictions';
COMMENT ON TABLE detection_patterns IS 'Manages scam detection patterns and rules';
COMMENT ON TABLE feedback_loop IS 'Captures user feedback for model improvement';
COMMENT ON TABLE performance_metrics IS 'Tracks daily performance metrics';
COMMENT ON TABLE api_keys IS 'Manages API authentication keys';
