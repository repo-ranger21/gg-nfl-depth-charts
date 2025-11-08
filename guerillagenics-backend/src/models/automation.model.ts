import { Schema, model } from 'mongoose';

const automationSchema = new Schema({
  name: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  status: {
    type: String,
    enum: ['active', 'inactive', 'pending'],
    default: 'active',
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
  kpis: [{
    type: Schema.Types.ObjectId,
    ref: 'KPI',
  }],
  rolloutPlans: [{
    type: Schema.Types.ObjectId,
    ref: 'RolloutPlan',
  }],
});

automationSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

const Automation = model('Automation', automationSchema);

export default Automation;