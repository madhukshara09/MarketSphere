class DecisionImpactEngine:

    def recommend(self,
                  segment,
                  spending,
                  purchases):

        if segment=="Premium VIP Customers":

            return{

                "Recommendation":
                "Launch Premium Loyalty Program",

                "Priority":
                "High",

                "Expected Impact":
                "Increase customer retention by 12-18%",

                "Confidence":
                "91%"
            }

        elif segment=="Loyal Customers":

            return{

                "Recommendation":
                "Cross-sell complementary products",

                "Priority":
                "Medium",

                "Expected Impact":
                "Increase Average Order Value by 10-15%",

                "Confidence":
                "87%"
            }

        elif segment=="Dormant Customers":

            return{

                "Recommendation":
                "Run Win-Back Campaign",

                "Priority":
                "High",

                "Expected Impact":
                "Recover 8-12% inactive customers",

                "Confidence":
                "83%"
            }

        else:

            return{

                "Recommendation":
                "Offer introductory discounts",

                "Priority":
                "Medium",

                "Expected Impact":
                "Improve first-time conversion",

                "Confidence":
                "79%"
            }