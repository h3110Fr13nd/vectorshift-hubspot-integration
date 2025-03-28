import { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Typography,
    Chip,
} from '@mui/material';
import axios from 'axios';

const endpointMapping = {
    'Notion': 'notion',
    'Airtable': 'airtable',
    'HubSpot': 'hubspot',
};

export const DataForm = ({ integrationType, credentials, loadedData: initialData, setLoadedData: setParentLoadedData }) => {
    const [loadedData, setLoadedData] = useState(initialData || null);
    const endpoint = endpointMapping[integrationType];

    // Update local state when props change
    useEffect(() => {
        setLoadedData(initialData);
    }, [initialData]);

    const handleLoad = async () => {
        try {
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(credentials));
            const response = await axios.post(`http://localhost:8000/integrations/${endpoint}/load`, formData);
            const data = response.data;
            setLoadedData(data);
            if (setParentLoadedData) {
                setParentLoadedData(data);
            }
            console.log(data);
        } catch (e) {
            alert(e?.response?.data?.detail);
        }
    }

    const handleClearData = () => {
        setLoadedData(null);
        if (setParentLoadedData) {
            setParentLoadedData(null);
        }
    };

    // Helper function to format dates
    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString();
    };

    return (
        <Box 
            display='flex' 
            justifyContent='center' 
            alignItems='center' 
            flexDirection='column' 
            width='100%' 
            sx={{ px: 2, maxWidth: '100vw' }}
        >
            <Box display='flex' flexDirection='column' width='100%' sx={{ maxWidth: '1200px', margin: '0 auto' }}>
                {loadedData && loadedData.length > 0 ? (
                    <TableContainer 
                        component={Paper} 
                        sx={{ 
                            mt: 2, 
                            maxHeight: 440,
                            overflowX: 'auto',
                            boxShadow: 3,
                            borderRadius: 2,
                            width: '100%',
                            maxWidth: '100%',
                            '&::-webkit-scrollbar': {
                                width: '10px',
                                height: '10px',
                            },
                            '&::-webkit-scrollbar-thumb': {
                                backgroundColor: 'rgba(0,0,0,.2)',
                                borderRadius: '10px',
                            }
                        }}
                    >
                        <Table stickyHeader aria-label="loaded data table" sx={{ tableLayout: 'fixed' }}>
                            <TableHead>
                                <TableRow>
                                    <TableCell width="150px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>ID</TableCell>
                                    <TableCell width="120px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Type</TableCell>
                                    <TableCell width="100px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Directory</TableCell>
                                    <TableCell width="150px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Parent</TableCell>
                                    <TableCell width="150px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Parent ID</TableCell>
                                    <TableCell width="150px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Name</TableCell>
                                    <TableCell width="180px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Created</TableCell>
                                    <TableCell width="180px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Modified</TableCell>
                                    <TableCell width="150px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>URL</TableCell>
                                    <TableCell width="120px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>MIME Type</TableCell>
                                    <TableCell width="120px" sx={{ fontWeight: 'bold', fontSize: '1rem', padding: '16px', backgroundColor: '#f5f5f5' }}>Visibility</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {loadedData.map((row, index) => (
                                    <TableRow
                                        key={row.id || index}
                                        sx={{ 
                                            '&:nth-of-type(odd)': { backgroundColor: 'rgba(0, 0, 0, 0.03)' },
                                            '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.07)' },
                                            transition: 'background-color 0.2s ease'
                                        }}
                                    >
                                        <TableCell 
                                            component="th" 
                                            scope="row" 
                                            sx={{ 
                                                padding: '16px', 
                                                overflow: 'hidden', 
                                                textOverflow: 'ellipsis', 
                                                whiteSpace: 'nowrap' 
                                            }}
                                        >
                                            {row.id || '-'}
                                        </TableCell>
                                        <TableCell sx={{ padding: '16px' }}>
                                            <Chip 
                                                label={row.type || 'Unknown'} 
                                                size="small" 
                                                color={row.type === 'Contact' ? 'primary' : 'secondary'}
                                                variant="outlined"
                                                sx={{ fontWeight: 'medium', padding: '8px 4px' }}
                                            />
                                        </TableCell>
                                        <TableCell sx={{ padding: '16px' }}>
                                            {row.directory !== undefined ? (
                                                <Chip 
                                                    label={row.directory ? 'Yes' : 'No'} 
                                                    color={row.directory ? 'info' : 'default'}
                                                    size="small"
                                                    sx={{ padding: '6px 3px' }}
                                                />
                                            ) : '-'}
                                        </TableCell>
                                        <TableCell sx={{ 
                                            padding: '16px', 
                                            overflow: 'hidden', 
                                            textOverflow: 'ellipsis', 
                                            whiteSpace: 'nowrap' 
                                        }}>
                                            {row.parent_path_or_name || '-'}
                                        </TableCell>
                                        <TableCell sx={{ 
                                            padding: '16px', 
                                            overflow: 'hidden', 
                                            textOverflow: 'ellipsis', 
                                            whiteSpace: 'nowrap' 
                                        }}>
                                            {row.parent_id || '-'}
                                        </TableCell>
                                        <TableCell sx={{ 
                                            padding: '16px', 
                                            overflow: 'hidden', 
                                            textOverflow: 'ellipsis', 
                                            whiteSpace: 'nowrap' 
                                        }}>
                                            {row.name || '-'}
                                        </TableCell>
                                        <TableCell sx={{ padding: '16px' }}>{formatDate(row.creation_time)}</TableCell>
                                        <TableCell sx={{ padding: '16px' }}>{formatDate(row.last_modified_time)}</TableCell>
                                        <TableCell sx={{ 
                                            padding: '16px', 
                                            overflow: 'hidden', 
                                            textOverflow: 'ellipsis', 
                                            whiteSpace: 'nowrap' 
                                        }}>
                                            {row.url || '-'}
                                        </TableCell>
                                        <TableCell sx={{ 
                                            padding: '16px', 
                                            overflow: 'hidden', 
                                            textOverflow: 'ellipsis', 
                                            whiteSpace: 'nowrap' 
                                        }}>
                                            {row.mime_type || '-'}
                                        </TableCell>
                                        <TableCell sx={{ padding: '16px' }}>
                                            {row.visibility !== undefined ? (
                                                <Chip 
                                                    label={row.visibility ? 'Visible' : 'Hidden'} 
                                                    color={row.visibility ? 'success' : 'error'}
                                                    size="small"
                                                    sx={{ padding: '6px 3px' }}
                                                />
                                            ) : '-'}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                ) : loadedData ? (
                    <Typography sx={{ mt: 2, textAlign: 'center' }}>No data available</Typography>
                ) : null}
                
                <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'center' }}>
                    <Button
                        onClick={handleLoad}
                        variant='contained'
                        sx={{ py: 1.2, px: 3, fontWeight: 'bold' }}
                        disabled={!credentials}
                    >
                        Load Data
                    </Button>
                    <Button
                        onClick={handleClearData}
                        variant='outlined'
                        color="secondary"
                        sx={{ py: 1.2, px: 3 }}
                        disabled={!loadedData}
                    >
                        Clear Data
                    </Button>
                </Box>
            </Box>
        </Box>
    );
}
