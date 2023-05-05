import Box from '@mui/material/Box';
import LinearProgress from '@mui/material/LinearProgress';

export default function LinearIndeterminate({ isLoading }: { isLoading: boolean }) {
    return (
        <>
            {
                isLoading
                    ?
                    <Box sx={{ width: '100%' }} >
                        <LinearProgress />
                    </Box >
                    :
                    <div style={{ height: '4px' }}></div>
            }
        </>
    );
}