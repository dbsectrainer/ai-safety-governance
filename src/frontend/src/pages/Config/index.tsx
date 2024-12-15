import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import { useState } from 'react';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`config-tabpanel-${index}`}
      aria-labelledby={`config-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const Config = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configuration Management
      </Typography>
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="configuration tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="General Settings" />
          <Tab label="Security" />
          <Tab label="Integrations" />
          <Tab label="Notifications" />
        </Tabs>
        
        <TabPanel value={tabValue} index={0}>
          <Typography>General platform settings and configurations</Typography>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Typography>Security settings and access controls</Typography>
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <Typography>Third-party integrations and API configurations</Typography>
        </TabPanel>
        
        <TabPanel value={tabValue} index={3}>
          <Typography>Notification preferences and alert settings</Typography>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default Config;
