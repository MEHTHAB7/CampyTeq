# CampyTeq Computer Vision Gateway Service

> Scheduled for Phase 8 implementation.

## Overview
A standalone microservice designed for high-throughput RTSP video ingestion, YOLO person detection, and authorized face embedding matching.

## Architecture
- Never streams raw CCTV video through the main Django application.
- Ingests RTSP feeds from configured zone cameras.
- Performs detection and edge inference.
- Posts lightweight detection events (`camera_id`, `zone_id`, `student_id`, `confidence_score`, `timestamp`) to `/api/v1/detections/` with secure mTLS/API key authorization.
