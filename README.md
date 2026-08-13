# E-Commerce Data Cleaning Project

## Overview
This project takes a realistic messy e-commerce orders dataset and cleans it into an analysis-ready format using Python and pandas. The goal was to practice real-world data cleaning skills: handling duplicates, inconsistent formatting, missing values, invalid entries, and mixed date formats.

## Problem
The raw dataset (`messy_orders.csv`) contained common real-world data quality issues:
- Duplicate order records
- Inconsistent text casing (e.g. "electronics" vs "Electronics" vs "ELECTRONICS")
- Extra whitespace in names and column headers
- Missing values in customer name, email, quantity, and price
- Order dates in four different formats (e.g. `2024-01-05`, `01/06/2024`, `2024/01/09`, `13-01-2024`)
- Invalid values (negative quantity, an unrealistic price outlier)

## What I Did
- Standardized column names and text formatting (casing, whitespace)
- Identified and removed duplicate orders
- Parsed and unified inconsistent date formats
- Handled missing values using context-appropriate strategies (e.g. category-level median price instead of a blanket fill)
- Flagged
