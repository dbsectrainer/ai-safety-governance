import { Box, Typography, Grid, Paper } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Sample data - will be replaced with real-time data
const performanceData = [
  { time: '00:00', value: 65 },
  { time: '04:00', value: 75 },
  { time: '08:00', value: 85 },
  { time: '12:00', value: 78 },
  { time: '16:00', value: 90 },
  { time: '20:00', value: 82 },
  { time: '24:00', value: 70 },
];

const Monitoring = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Monitoring
      </Typography>
      
      <Grid container spacing={3}>
        {/* Performance Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Performance
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#8884d8" 
                    name="Performance Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Metrics Overview */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Resource Usage
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                CPU Usage: 45%
              </Typography>
              <Typography variant="body1" gutterBottom>
                Memory Usage: 62%
              </Typography>
              <Typography variant="body1" gutterBottom>
                Storage Usage: 38%
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Active Models */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Model Status
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" gutterBottom>
                Active Models: 12
              </Typography>
              <Typography variant="body1" gutterBottom>
                Average Response Time: 245ms
              </Typography>
              <Typography variant="body1" gutterBottom>
                Error Rate: 0.02%
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Monitoring;
