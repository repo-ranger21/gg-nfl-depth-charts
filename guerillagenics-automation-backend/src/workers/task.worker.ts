export const taskWorker = async (task: any) => {
    try {
        // Process the task here
        console.log(`Processing task: ${JSON.stringify(task)}`);
        
        // Simulate task processing
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        console.log(`Task completed: ${JSON.stringify(task)}`);
    } catch (error) {
        console.error(`Error processing task: ${error}`);
        throw error;
    }
};