import streamlit as st
import pandas as pd
import time



st.set_page_config(page_title="Zinseszinsrechner", layout="centered", page_icon=":chart_with_upwards_trend:")
st.header("💶 Zinseszinsrechner")  

tab1, tab2 = st.tabs(["➗ Berechnung", "📈 Grafik"])
with tab1:
    with st.expander("Details zur Berechnung"):
        st.write("""
                 - Äquivalenter Zinssatz
                - vorschüssig = Intervallbeginn
                 - nachschüssig = Intervallende
                 - Steuern werden idR. am Ende der Berechnung abgeführt
                 """)
        
    st.subheader("Input")
    row1_col1, row1_col2 = st.columns(2)
    starting_capital = row1_col1.number_input("Anfangskapital", min_value=0.00)
    years = row1_col2.number_input("Anlagezeitraum (in Jahren)", min_value=0)
    

    row2_col1, row2_col2 = st.columns(2)
    annual_interest_rate = row2_col1.number_input("Zinsniveau p.a. (in %)", min_value=0.00)
    compounding_frequency_str = row2_col2.selectbox("Verzinsungsintervall", ["monatlich", "quartalsweise", "halbjährlich", "jährlich"])
    

    row3_col1, row3_col2 = st.columns(2)
    savings_rate = row3_col1.number_input("Sparrate", min_value=0.00)
    savings_rate_frequency_str = row3_col2.selectbox("Ratenintervall", ["monatlich", "quartalsweise", "halbjährlich", "jährlich"])
    
    
    row4_col1, row4_col2 = st.columns(2)
    tax_rate = row4_col1.number_input("KESt (in %)", min_value=0.00)
    payment_modality_str = row4_col2.selectbox("Ratenzeitpunkt", ["vorschüssig", "nachschüssig"])

    tax_toggle = st.toggle("Steuern pro Zinsperiode")
    
    
    savings_rate_frequency_map = {"monatlich": 1, "quartalsweise": 3, "halbjährlich": 6, "jährlich": 12}
    savings_rate_frequency = savings_rate_frequency_map.get(savings_rate_frequency_str, None)
    
    compounding_frequency_map = {"monatlich": 1, "quartalsweise": 3, "halbjährlich": 6, "jährlich": 12}
    compounding_frequency = compounding_frequency_map.get(compounding_frequency_str, None)
    
    payment_modality_map = {"vorschüssig": 1, "nachschüssig": 0}
    payment_modality = payment_modality_map.get(payment_modality_str, None)
      
    
    
    class CompoundInterestCalculator:
        def __init__(self, starting_capital, years, annual_interest_rate, compounding_frequency, savings_rate, savings_rate_frequency, tax_rate, payment_modality):
 
            self.starting_capital = starting_capital
            self.years = years
            self.months = years * 12
            
            self.annual_interest_rate = annual_interest_rate / 100
            self.compounding_frequency = compounding_frequency
            
            self.savings_rate = savings_rate
            self.savings_rate_frequency = savings_rate_frequency
            
            self.tax_rate = (tax_rate / 100)
            self.payment_modality = payment_modality


        def __repr__(self) -> str:
            return (
                f"CompoundInterestCalculator("
                f"starting_capital={self.starting_capital}, "
                f"years={self.years}, "
                f"annual_interest_rate={self.annual_interest_rate * 100:.2f}, "
                f"compounding_frequency={self.compounding_frequency}, "
                f"savings_rate={self.savings_rate}, "
                f"savings_rate_frequency={self.savings_rate_frequency}, "
                f"tax_rate={self.tax_rate * 100:.2f}, "
                f"payment_modality={self.payment_modality}"
                f")"
                )
        
        
        def compute_gross_values(self) -> float:
            final_value = 0.0
            number_of_payments = 0
            tgc = 0.0
            
            for months in range(1, self.months + 1):
                
                # vorschüssig
                if payment_modality == 1:
                    if (months - 1) % self.savings_rate_frequency == 0:
                        final_value += self.savings_rate
                        number_of_payments += 1

                # Verzinsung
                if months % self.compounding_frequency == 0:
                    final_value *= (1 + self.annual_interest_rate) ** (1 / (12 / self.compounding_frequency))
                
                # nachschüssig
                if payment_modality == 0:
                    if months % self.savings_rate_frequency == 0:
                        final_value += self.savings_rate
                        number_of_payments += 1
            
            tgc = final_value + (self.starting_capital * ((1 + self.annual_interest_rate) ** self.years))
            total_inpayments = self.savings_rate * number_of_payments + self.starting_capital
            
            return tgc, total_inpayments
        
        
        def compute_net_values(self, *args) -> float:
            
            # Steuer nach Verzinsungsart
            if tax_toggle:
                final_value_1 = 0.0
                tax_1 = []
                
                final_value_1 = starting_capital
                # Grundkapital versteuern (Part 1)
                for months in range(1, self.months + 1):

                    # Verzinsung
                    if months % self.compounding_frequency == 0:
                        # Zinsen und Steuern berechnen
                        interest_per_period_1 = (final_value_1 * (1 + self.annual_interest_rate) ** (1 / (12 / self.compounding_frequency))) - final_value_1
                        tax_per_period_1 = interest_per_period_1 * self.tax_rate
                        tax_1.append(tax_per_period_1)
                        
                        # normale Verzinsung und danach Steuern abziehen
                        final_value_1 *= (1 + self.annual_interest_rate) ** (1 / (12 / self.compounding_frequency))
                        final_value_1 -= tax_per_period_1
                        
 
                
                final_value_2 = 0.0
                tax_2 = []
                # Sparrate versteuern (Part 2)
                for months in range(1, self.months + 1):
                    
                    # vorschüssig
                    if payment_modality == 1:
                        if (months - 1) % self.savings_rate_frequency == 0:
                            final_value_2 += self.savings_rate

                    # Verzinsung
                    if months % self.compounding_frequency == 0:
                        # Zinsen und Steuern berechnen
                        interest_per_period_2 = (final_value_2 * (1 + self.annual_interest_rate) ** (1 / (12 / self.compounding_frequency))) - final_value_2
                        tax_per_period_2 = interest_per_period_2 * self.tax_rate
                        tax_2.append(tax_per_period_2)
                        
                        # normale Verzinsung und danach Steuern abziehen
                        final_value_2 *= (1 + self.annual_interest_rate) ** (1 / (12 / self.compounding_frequency))
                        final_value_2 -= tax_per_period_2
                        
                    
                    # nachschüssig
                    if payment_modality == 0:
                        if months % self.savings_rate_frequency == 0:
                            final_value_2 += self.savings_rate
              
                eat =  final_value_1 + final_value_2
                overall_tax = (sum(tax_1) + sum(tax_2))
            
            # Steuer einmalig am Ende
            else:
                if not args:
                    gross_values = self.compute_gross_values()
                    tgc, total_inpayments = gross_values
                else:
                    tgc, total_inpayments = args
                
                eat = tgc - ((tgc - total_inpayments) * self.tax_rate)
                overall_tax = (tgc - total_inpayments) * self.tax_rate
                
            return eat, overall_tax
        

    
    # creating an object
    compute_metrics = CompoundInterestCalculator(starting_capital, years, annual_interest_rate, compounding_frequency, savings_rate, savings_rate_frequency, tax_rate, payment_modality)
    # call methods with object for results
    result_1, result_3 = compute_metrics.compute_gross_values() # Gesamtkapital (Brutto), Einzahlungen
    result_4 = result_1 - result_3 # Zinsgewinn (Brutto)

    result_2, result_6 = compute_metrics.compute_net_values() # Gesamtkapital (Netto), Steuer
    result_5 = result_2 - result_3 # Zinsgewinn (Netto)
    
    
    st.write("####")

    # displaying results
    st.subheader("Ergebnisse")
    st.markdown(
    f"""
    
    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
        <strong>Gesamtkapital (Brutto):</strong>
        <span>{result_1:,.2f} €</span>
    </div>
    
    <div style='display: flex; justify-content: space-between; margin-bottom: 25px;'>
        <strong>Gesamtkapital (Netto):</strong>
        <span>{result_2:,.2f} €</span>
    </div>
    
    <div style='display: flex; justify-content: space-between; margin-bottom: 25px;'>
        <strong>Einzahlungen:</strong>
        <span>{result_3:,.2f} €</span>
    </div>
    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
        <strong>Zinsgewinn (Brutto):</strong>
        <span>{result_4:,.2f} €</span>
    </div>
    
    <div style='display: flex; justify-content: space-between; margin-bottom: 25px;'>
        <strong>Zinsgewinn (Netto):</strong>
        <span>{result_5:,.2f} €</span>
    </div>
    
    <div style='display: flex; justify-content: space-between;'>
        <strong>Steuer:</strong>
        <span>{result_6:,.2f} €</span>
    </div>
    """, unsafe_allow_html=True)