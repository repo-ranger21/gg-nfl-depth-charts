import { schedule } from 'node-cron';

export const startScheduler = () => {
    // Schedule a task to run every minute
    schedule('* * * * *', () => {
        console.log('Running scheduled task...');
        // Add your automation logic here
    });
};