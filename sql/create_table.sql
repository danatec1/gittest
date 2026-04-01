CREATE TABLE IF NOT EXISTS data_go_dataset_stats (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_type VARCHAR(50),
    title VARCHAR(1000),
    view_count INT,
    metric_name VARCHAR(50),
    metric_value INT,
    keyword VARCHAR(255),
    page_no INT,
    collected_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_data_go_dataset (data_type, title, collected_at)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
