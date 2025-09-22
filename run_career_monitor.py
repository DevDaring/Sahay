#!/usr/bin/env python3
"""
Script to run career monitoring service periodically
"""

import time
import schedule
import logging
from services.career_monitoring_service import CareerMonitoringService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/career_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_career_monitoring():
    """Run the career monitoring service"""
    try:
        logger.info("Starting scheduled career monitoring...")
        service = CareerMonitoringService()
        service.monitor_and_update()
        logger.info("Scheduled career monitoring completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled career monitoring: {e}", exc_info=True)

def main():
    """Main function to set up and run the scheduler"""
    logger.info("Career Monitoring Service Scheduler Started")
    
    # Schedule the service to run every 6 hours
    schedule.every(6).hours.do(run_career_monitoring)
    
    # Also run once immediately
    run_career_monitoring()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
