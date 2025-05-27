import React from 'react';
import { FormControl, InputLabel, Select, MenuItem, SelectChangeEvent } from '@mui/material';
import { Team } from '../types';

interface TeamSelectorProps {
  label: string;
  teams: Team[];
  selectedTeam: Team | null;
  onTeamSelect: (team: Team) => void;
}

const TeamSelector: React.FC<TeamSelectorProps> = ({
  label,
  teams,
  selectedTeam,
  onTeamSelect,
}) => {
  const handleChange = (event: SelectChangeEvent) => {
    const team = teams.find(t => t.id.toString() === event.target.value);
    if (team) {
      onTeamSelect(team);
    }
  };

  return (
    <FormControl fullWidth>
      <InputLabel>{label}</InputLabel>
      <Select
        value={selectedTeam?.id.toString() || ''}
        label={label}
        onChange={handleChange}
      >
        {teams.map((team) => (
          <MenuItem key={team.id} value={team.id.toString()}>
            {team.name} ({team.abbreviation})
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default TeamSelector; 