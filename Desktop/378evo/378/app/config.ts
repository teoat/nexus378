
export const appConfig = {
    version: "1.2.0",
    standardFields: [
        "date", "description", "debit", "credit", 
        "bankAccount", "category", "timeline", "numbering", "comment"
    ],
    matchingTolerances: {
        dateToleranceDays: 2,
        amountTolerancePercentage: 1,
    }
};
