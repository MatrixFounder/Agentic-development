/**
 * Calculates total price.
 * 
 * @param {number} price - Base price.
 * @param {number} rate - Tax rate.
 * @returns {number} Total price.
 */
function calculate(price: number, rate: number): number {
    return price * (1 + rate);
}
