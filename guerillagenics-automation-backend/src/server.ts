import express from 'express';
import { setRoutes } from './routes/index';
import { errorMiddleware } from './middlewares/error.middleware';
import { loadEnv } from './config/env';

const app = express();
loadEnv();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

setRoutes(app);

app.use(errorMiddleware);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});