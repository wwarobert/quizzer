/**
 * Motivational Messages Configuration
 * Provides encouraging messages based on quiz performance
 */

export const motivationalMessages = {
    perfect: [
        "🎉 Perfect Score! You're absolutely crushing it!",
        "💯 Flawless! Your expertise is truly impressive!",
        "🌟 Outstanding! A perfect demonstration of mastery!",
        "🏆 Perfect execution! You've reached the pinnacle!"
    ],
    excellent: [ // 90-99%
        "🌟 Excellent work! You're clearly on top of your game!",
        "💪 Nearly perfect! Your dedication shows!",
        "✨ Exceptional performance! Just shy of perfection!",
        "🚀 Impressive! You're reaching for the stars!"
    ],
    good: [ // 80-89%
        "✅ Well done! You've passed with solid knowledge!",
        "👍 Good job! You're demonstrating strong understanding!",
        "💚 Nice work! You've got the fundamentals down!",
        "🎯 Passed! Keep up the good momentum!"
    ],
    close: [ // 70-79%
        "😊 Close! You're almost there! Review and try again!",
        "📚 Not bad! A bit more study and you'll ace it!",
        "💪 Keep pushing! You're on the right track!",
        "🔄 Good effort! One more review should do it!"
    ],
    failed: [ // <70%
        "📖 Don't give up! Learning takes time and practice.",
        "💡 This is a learning opportunity! Review and come back stronger!",
        "🌱 Every expert was once a beginner. Keep studying!",
        "🔍 Take time to review. You'll get there with persistence!",
        "💪 Challenges make you stronger! Don't stop now!"
    ]
};

/**
 * Get a random motivational message based on score percentage
 * @param {number} scorePercentage - The quiz score as a percentage (0-100)
 * @returns {string} A motivational message
 */
export function getMotivationalMessage(scorePercentage) {
    let messages;
    if (scorePercentage === 100) {
        messages = motivationalMessages.perfect;
    } else if (scorePercentage >= 90) {
        messages = motivationalMessages.excellent;
    } else if (scorePercentage >= 80) {
        messages = motivationalMessages.good;
    } else if (scorePercentage >= 70) {
        messages = motivationalMessages.close;
    } else {
        messages = motivationalMessages.failed;
    }
    return messages[Math.floor(Math.random() * messages.length)];
}
