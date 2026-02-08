---
title: Kidney Compass Backend
ecolor: green
emoji: 🧠
sdk: docker
sdk_version: 20.10.24
app_file: app.py
pinned: false
description: FastAPI backend for Kidney Compass application with food classification and recipe generation
---

# Kidney Compass Backend

This is the backend service for Kidney Compass, a health management application for people with kidney diseases.

## Features

- **Food Classification**: Classify foods based on kidney health impact
- **Recipe Generation**: Generate kidney-friendly recipes
- **Food Whitelist/Blacklist**: Manage approved and restricted foods
- **Health Tracking**: Track health metrics and daily records
- **AI Integration**: Uses Gemini API for food classification

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - Detailed health check
- `POST /api/classify` - Classify food items
- `GET /api/food-whitelist` - Get approved foods
- `GET /api/food-blacklist` - Get restricted foods
- `POST /api/recipe` - Generate kidney-friendly recipes

## Technologies

- **Backend**: FastAPI, Python 3.9+
- **Database**: Supabase
- **AI**: Google Gemini API
- **Deployment**: Hugging Face Spaces

## Environment Variables

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `GEMINI_API_KEY` - Google Gemini API key
