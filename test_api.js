// Test API calls from console
const testSignup = async () => {
    const data = {
        firstName: 'TuğbaTest',
        lastName: 'TestAdi',
        email: `test_${Date.now()}@example.com`,
        password: 'Test123456',
        phone: '5551234567'
    };
    
    console.log('Testing signup with:', data);
    try {
        const response = await fetch('http://localhost:5000/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        console.log('Response:', response.status, result);
        return result;
    } catch (error) {
        console.error('Error:', error);
    }
};

testSignup();
