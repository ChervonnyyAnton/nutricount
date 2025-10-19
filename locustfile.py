#!/usr/bin/env python3
"""
Locust performance test file for Nutrition Tracker
"""

from locust import HttpUser, task, between


class NutritionTrackerUser(HttpUser):
    """Simulate user interactions with the nutrition tracker"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        self.client.get("/")
    
    @task(3)
    def view_homepage(self):
        """Most common task - view homepage"""
        self.client.get("/")
    
    @task(2)
    def view_products(self):
        """View products list"""
        self.client.get("/api/products")
    
    @task(2)
    def view_dishes(self):
        """View dishes list"""
        self.client.get("/api/dishes")
    
    @task(1)
    def view_stats(self):
        """View daily stats"""
        self.client.get("/api/stats/daily")
    
    @task(1)
    def view_fasting_status(self):
        """View fasting status"""
        self.client.get("/api/fasting/status")
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")
    
    @task(1)
    def view_metrics(self):
        """View Prometheus metrics"""
        self.client.get("/metrics")
