export class HealthController {
    public getHealth(req, res) {
        res.status(200).json({ status: 'UP' });
    }
}