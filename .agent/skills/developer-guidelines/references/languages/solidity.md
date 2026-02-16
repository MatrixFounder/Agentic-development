# Solidity Developer Guidelines

## Security First
- **Checks-Effects-Interactions:** ALWAYS update state variables BEFORE making external calls to prevent reentrancy.
- **Access Control:** Explicitly define function visibility (`external`, `public`, `internal`, `private`). Use `Ownable` or `AccessControl` for restricted functions.
- **Overflow/Underflow:** Rely on Solidity 0.8+ built-in checks.


## Gas Optimization
- **Pack Storage**: Order state variables to fit 32 bytes (e.g., `uint128, uint128` next to each other).
- **Data Types**: Use `uint256` for calculations (cheaper than `uint8` due to padding), but packed types in storage.
- **Memory vs Calldata**: Use `calldata` for read-only function arguments (avoids copying).
- **Events**: Use events for data storage when on-chain access isn't required (much cheaper).
- **Custom Errors**: Use `error InsufficientBalance();` instead of `require(..., "Long string")`.

## Testing Patterns (Hardhat/Foundry)
- **Mainnet Forking**: Test against real state.
- **Fuzzing**: Use Echidna or Foundry (`testFuzz`) to check invariants.
- **Console.log**: Use `hardhat/console.sol` for debugging.

```javascript
// Hardhat Example
it("Should revert on reentrancy", async function () {
  const Attacker = await ethers.getContractFactory("Attacker");
  await expect(attacker.attack()).to.be.revertedWith("ReentrancyGuard: reentrant call");
});
```

## Documentation Standards (NatSpec)
- **Required**: `@title`, `@author`, `@notice` (user), `@dev` (developer).
- **Params**: `@param` for all arguments.
- **Returns**: `@return` for all return values.

## Design Patterns
- **Pull over Push**: Never loop through arrays to send ETH. Let users withdraw (Pull) to prevent DoS if one transfer fails.
