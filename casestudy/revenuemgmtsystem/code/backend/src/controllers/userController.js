const users = [
    { id: 1, name: 'Alex Johnson', email: 'alex.j@example.com', role: 'Admin', status: 'Active', lastActive: '2 mins ago' },
    { id: 2, name: 'Sarah Miller', email: 'sarah.m@example.com', role: 'Manager', status: 'Active', lastActive: '1 hr ago' },
    { id: 3, name: 'Michael Chen', email: 'michael.c@example.com', role: 'Analyst', status: 'Inactive', lastActive: '2 days ago' },
];

let idpConfig = {
    enabled: false,
    provider: 'google',
    clientId: '',
    issuerUrl: 'https://accounts.google.com',
    metadataUrl: ''
};

exports.getUsers = (req, res) => {
    res.json(users);
};

exports.inviteUser = (req, res) => {
    const { name, email, role } = req.body;
    const newUser = {
        id: users.length + 1,
        name,
        email,
        role,
        status: 'Pending',
        lastActive: 'Never'
    };
    users.push(newUser);
    res.json({ message: 'Invitation sent', user: newUser });
};

exports.getIDPConfig = (req, res) => {
    res.json(idpConfig);
};

exports.updateIDPConfig = (req, res) => {
    const config = req.body;
    idpConfig = { ...idpConfig, ...config };
    res.json({ message: 'IDP Configuration Updated', config: idpConfig });
};
