describe('AuthService', () => {
    let authService;
    let mockDatabase;

    // 1. Setup/Teardown
    beforeEach(() => {
        mockDatabase = {
            findUser: jest.fn(),
        };
        authService = new AuthService(mockDatabase);
    });

    // 2. Clear Description: should [expected behavior] when [condition]
    it('should return token when credentials are valid', async () => {
        // Arrange
        const user = { id: 1, name: 'Test User' };
        mockDatabase.findUser.mockResolvedValue(user);

        // Act
        const token = await authService.login('user', 'pass');

        // Assert
        expect(token).toBeDefined();
        expect(mockDatabase.findUser).toHaveBeenCalledWith('user');
    });

    // 3. Error Case
    it('should throw error when user not found', async () => {
        // Arrange
        mockDatabase.findUser.mockResolvedValue(null);

        // Act & Assert
        await expect(authService.login('unknown', 'pass')).rejects.toThrow('User not found');
    });
});

// Mock Class for Context
class AuthService {
    constructor(db) { this.db = db; }
    async login(u, p) {
        const user = await this.db.findUser(u);
        if (!user) throw new Error('User not found');
        return "token";
    }
}
