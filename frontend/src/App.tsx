import React, { useState } from 'react';
import { ThemeProvider, CssBaseline, IconButton, Box } from '@mui/material';
import { lightTheme, darkTheme } from './theme';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import MatchPrediction from './components/MatchPrediction';
import TeamComparison from './components/TeamComparison';
import HistoricalPredictions from './components/HistoricalPredictions';
import { Tab, Tabs, AppBar, Toolbar, Typography } from '@mui/material';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <ThemeProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              NBA Match Predictor
            </Typography>
            <IconButton color="inherit" onClick={toggleTheme}>
              {isDarkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Toolbar>
          <Tabs value={currentTab} onChange={handleTabChange} centered>
            <Tab label="Match Prediction" />
            <Tab label="Team Comparison" />
            <Tab label="Historical Predictions" />
          </Tabs>
        </AppBar>

        <Box sx={{ p: 3 }}>
          <ErrorBoundary>
            {currentTab === 0 && <MatchPrediction />}
            {currentTab === 1 && <TeamComparison />}
            {currentTab === 2 && <HistoricalPredictions />}
          </ErrorBoundary>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App; 