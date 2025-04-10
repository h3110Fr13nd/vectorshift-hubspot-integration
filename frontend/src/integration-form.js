import { useState } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubSpotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';

const integrationMapping = {
    'Notion': NotionIntegration,
    'Airtable': AirtableIntegration,
    'HubSpot': HubSpotIntegration,
};

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const [previousData, setPreviousData] = useState(null);
    const CurrIntegration = integrationMapping[currType];

    const handleIntegrationChange = (e, value) => {
        if (value !== currType) {
            if (integrationParams?.loadedData) {
                setPreviousData(integrationParams.loadedData);
            }
            
            setIntegrationParams(prev => ({
                loadedData: prev.loadedData, 
                previousType: prev.type      
            }));
            
            setCurrType(value);
        }
    };

  return (
    <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%' }}>
        <Box display='flex' flexDirection='column'>
        <TextField
            label="User"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            sx={{mt: 2}}
        />
        <TextField
            label="Organization"
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            sx={{mt: 2}}
        />
        <Autocomplete
            id="integration-type"
            options={Object.keys(integrationMapping)}
            sx={{ width: 300, mt: 2 }}
            renderInput={(params) => <TextField {...params} label="Integration Type" />}
            onChange={handleIntegrationChange}
            value={currType}
        />
        </Box>
        {currType && 
        <Box>
            <CurrIntegration 
                user={user} 
                org={org} 
                integrationParams={{
                    ...integrationParams,
                    credentials: integrationParams?.type === currType ? integrationParams.credentials : null
                }} 
                setIntegrationParams={setIntegrationParams} 
            />
        </Box>
        }
        {(integrationParams?.credentials || integrationParams?.loadedData || previousData) && 
        <Box sx={{mt: 2, width: '100%'}}>
            <DataForm 
                integrationType={integrationParams?.type || integrationParams?.previousType} 
                credentials={integrationParams?.credentials}
                loadedData={integrationParams?.loadedData || previousData}
                setLoadedData={(data) => setIntegrationParams(prev => ({...prev, loadedData: data}))}
            />
        </Box>
        }
    </Box>
  );
}
