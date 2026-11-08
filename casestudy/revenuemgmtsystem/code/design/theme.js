/**
 * ZenithStays Design System - Theme Configuration
 * Usage: Import into Tailwind config or JS styling solution.
 */

export const theme = {
    colors: {
        primary: {
            royalBlue: '#003366',
            softTeal: '#008080',
        },
        background: {
            lightGray: '#F5F7FA',
            white: '#FFFFFF',
        },
        status: {
            success: '#28A745',
            warning: '#FFC107',
            danger: '#DC3545',
        },
        text: {
            dark: '#333333',
            muted: '#6C757D',
        }
    },
    typography: {
        fontFamily: {
            sans: ['Inter', 'Roboto', 'sans-serif'],
        },
        fontSize: {
            h1: '24px',
            h2: '20px',
            h3: '16px',
            body: '14px',
        }
    },
    borderRadius: {
        card: '8px',
        button: '4px',
    },
    shadows: {
        card: '0 2px 4px rgba(0,0,0,0.05)',
    }
};
