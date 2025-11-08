-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create soil_analysis table
CREATE TABLE soil_analysis (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    n_value DECIMAL(5, 2),
    p_value DECIMAL(5, 2),
    k_value DECIMAL(5, 2),
    ph_value DECIMAL(4, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create crops table
CREATE TABLE crops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_kannada VARCHAR(255),
    description TEXT,
    description_kannada TEXT
);

-- Create crop_recommendations table
CREATE TABLE crop_recommendations (
    id SERIAL PRIMARY KEY,
    crop_id INTEGER REFERENCES crops(id),
    min_n DECIMAL(5, 2),
    max_n DECIMAL(5, 2),
    min_p DECIMAL(5, 2),
    max_p DECIMAL(5, 2),
    min_k DECIMAL(5, 2),
    max_k DECIMAL(5, 2),
    min_ph DECIMAL(4, 2),
    max_ph DECIMAL(4, 2)
);

-- Create farming_tips table
CREATE TABLE farming_tips (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255),
    tip_title VARCHAR(255),
    tip_title_kannada VARCHAR(255),
    tip_content TEXT,
    tip_content_kannada TEXT
);

-- Create weather_data table
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    location VARCHAR(255),
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    description VARCHAR(255),
    description_kannada VARCHAR(255),
    icon VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert some sample data
INSERT INTO crops (name, name_kannada, description, description_kannada) VALUES
('Rice', 'ಭತ್ತ', 'A staple food for a large part of the world''s human population.', 'ವಿಶ್ವದ ಮಾನವ ಜನಸಂಖ್ಯೆಯ ಹೆಚ್ಚಿನ ಭಾಗಕ್ಕೆ ಪ್ರಧಾನ ಆಹಾರ.'),
('Wheat', 'ಗೋಧಿ', 'A cereal grain, which is a worldwide staple food.', 'ಒಂದು ಏಕದಳ ಧಾನ್ಯ, ಇದು ವಿಶ್ವಾದ್ಯಂತ ಪ್ರಧಾನ ಆಹಾರವಾಗಿದೆ.'),
('Maize', 'ಮೆಕ್ಕೆಜೋಳ', 'A large grain plant first domesticated by indigenous peoples in southern Mexico.', 'ದಕ್ಷಿಣ ಮೆಕ್ಸಿಕೋದ ಸ್ಥಳೀಯ ಜನರು ಮೊದಲು ಪಳಗಿಸಿದ ದೊಡ್ಡ ಧಾನ್ಯದ ಸಸ್ಯ.');

INSERT INTO crop_recommendations (crop_id, min_n, max_n, min_p, max_p, min_k, max_k, min_ph, max_ph) VALUES
(1, 80, 120, 40, 60, 40, 60, 5.5, 7.0),
(2, 100, 150, 50, 70, 50, 70, 6.0, 7.5),
(3, 80, 120, 40, 60, 20, 40, 5.8, 7.0);

INSERT INTO farming_tips (category, tip_title, tip_title_kannada, tip_content, tip_content_kannada) VALUES
('soil_health', 'Improve Soil Health', 'ಮಣ್ಣಿನ ಆರೋಗ್ಯವನ್ನು ಸುಧಾರಿಸಿ', 'Use compost and cover crops to improve soil structure and fertility.', 'ಮಣ್ಣಿನ ರಚನೆ ಮತ್ತು ಫಲವತ್ತತೆಯನ್ನು ಸುಧಾರಿಸಲು ಕಾಂಪೋಸ್ಟ್ ಮತ್ತು ಕವರ್ ಬೆಳೆಗಳನ್ನು ಬಳಸಿ.'),
('water_management', 'Efficient Water Use', 'ದಕ್ಷ ನೀರಿನ ಬಳಕೆ', 'Use drip irrigation to deliver water directly to the plant roots.', 'ಸಸ್ಯದ ಬೇರುಗಳಿಗೆ ನೇರವಾಗಿ ನೀರನ್ನು ತಲುಪಿಸಲು ಹನಿ ನೀರಾವರಿ ಬಳಸಿ.'),
('pest_control', 'Natural Pest Control', 'ನೈಸರ್ಗಿಕ ಕೀಟ ನಿಯಂತ್ರಣ', 'Introduce beneficial insects like ladybugs to control pests.', 'ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸಲು ಲೇಡಿಬಗ್‌ಗಳಂತಹ ಪ್ರಯೋಜನಕಾರಿ ಕೀಟಗಳನ್ನು ಪರಿಚಯಿಸಿ.');

INSERT INTO weather_data (location, temperature, humidity, description, description_kannada, icon) VALUES
('Bengaluru', 28.5, 65, 'Partly cloudy', 'ಭಾಗಶಃ ಮೋಡ', '02d');
