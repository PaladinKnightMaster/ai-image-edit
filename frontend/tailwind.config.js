module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" }
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        pulseSoft: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" }
        }
      },
      animation: {
        float: "float 12s ease-in-out infinite",
        "fade-up": "fadeUp 0.8s ease-out both",
        "pulse-soft": "pulseSoft 3s ease-in-out infinite"
      },
      boxShadow: {
        soft: "0 20px 60px rgba(15, 23, 42, 0.15)"
      }
    }
  },
  plugins: []
};
