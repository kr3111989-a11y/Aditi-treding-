class TradingAIBrain:
    def __init__(self):
        self.budget = 2000  # आपका फिक्स ट्रेडिंग बजट नियम
        
    def analyze_market_conditions(self, market_data):
        """
        यह बॉट का 'दिमाग' है जो 10 अलग-अलग लेयर्स पर मार्केट को परखेगा।
        """
        score = 0
        reasons = []

        # 1. ग्लोबल और सेंटीमेंट चेक (Global Cues)
        if market_data.get('global_trend') == 'Bullish':
            score += 1
            reasons.append("Global market is supportive.")

        # 2. टाइम-बेस्ड फिल्टर (No-Trade Zone check)
        if market_data.get('is_no_trade_time', False):
            return "HOLD", "Market is in No-Trade Zone (Opening volatility)."

        # 3. प्राइस एक्शन और ओपनिंग रेंज ब्रेकआउट (ORB)
        if market_data.get('price_breakout') == 'High_Broken':
            score += 2
            reasons.append("Opening range high broken.")

        # 4. टेक्निकल इंडिकेटर्स (VWAP & RSI)
        if market_data.get('price', 0) > market_data.get('vwap', 0):
            score += 1
            reasons.append("Price is above VWAP.")
            
        if 40 <= market_data.get('rsi', 50) <= 60:
            score += 1
            reasons.append("RSI is in healthy zone.")

        # 5. ऑप्शन चेन और PCR (Put-Call Ratio) विश्लेषण
        pcr = market_data.get('pcr', 1.0)
        if pcr > 1.2:
            score += 2
            reasons.append(f"PCR is bullish ({pcr}).")
        elif pcr < 0.8:
            score -= 2
            reasons.append(f"PCR is bearish ({pcr}).")

        # 6. ओपेन इंटरेस्ट (OI) वेलोसिटी और स्पाइक
        if market_data.get('oi_spike') == 'Call_Unwinding':
            score += 1
            reasons.append("Call unwinding detected (Bullish).")

        # 7. वोलटिलिटी और IV क्रश चेक
        if market_data.get('iv_status') == 'High_IV_Crush_Expected':
            return "AVOID", "Risk of IV Crush, do not buy options."

        # 8. मल्टी-टाइमफ्रेम कन्फ्लुएंस
        if not market_data.get('higher_timeframe_support', True):
            return "AVOID", "Higher timeframe resistance reached, trap risk!"

        # 9. ट्रैप डिटेक्शन (Fake Breakout check)
        if market_data.get('is_trap', False):
            return "AVOID", "Potential operator trap detected."

        # 10. जोखिम प्रबंधन (Risk & Budget Check - आपका ₹2000 का बजट नियम)
        if self.budget < 2000:
            return "STOP", "Insufficient budget or limit reached."

        # निर्णय लेना (Decision Matrix Based on Score)
        if score >= 4:
            return "BUY_CE", reasons
        elif score <= -2:
            return "BUY_PE", reasons
        else:
            return "WAIT", "Market is sideways, no clear setup."
