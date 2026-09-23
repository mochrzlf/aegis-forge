//+------------------------------------------------------------------+
//|                                         AegisRiskGuardianEA.mq5  |
//|                                  Copyright 2026, Aegis Forge     |
//|                      https://github.com/mochrzlf/aegis-forge     |
//+------------------------------------------------------------------+
#property copyright   "Aegis Forge"
#property link        "https://github.com/mochrzlf/aegis-forge"
#property version     "1.00"
#property description "Institutional Risk-First Expert Advisor Template."
#property description "Enforces dynamic lot sizing (1-2%), hard SL, and daily drawdown kill-switch."

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>

//--- Input Parameters (Risk & Capital Preservation Doctrine)
input group "--- Risk Management Guardrails ---"
input double   InpRiskPercent             = 1.0;     // Risk Per Trade % of Equity (Max 2.0%)
input double   InpMaxDailyDrawdownPercent = 5.0;     // Emergency Circuit Breaker Daily DD %
input int      InpMaxAllowedSpreadPoints  = 30;      // Max Allowed Spread (Points)
input int      InpStopLossPoints          = 500;     // Mandatory Hard Stop Loss (Points, >0)
input int      InpTakeProfitPoints        = 1000;    // Take Profit (Points)
input ulong    InpMagicNumber             = 100201;  // EA Magic Number

input group "--- Strategy Signal Configuration ---"
input int      InpFastMAPeriod            = 9;       // Fast MA Period
input int      InpSlowMAPeriod            = 21;      // Slow MA Period

//--- Global Variables
CTrade         m_trade;
CPositionInfo  m_position;
COrderInfo     m_order;
double         m_dayStartEquity           = 0.0;
datetime       m_currentDay               = 0;
bool           m_circuitBreakerTripped    = false;
int            m_fastMAHandle             = INVALID_HANDLE;
int            m_slowMAHandle             = INVALID_HANDLE;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // 1. Enforce Hard Stop Loss Requirement (Anti-Martingale Doctrine)
   if(InpStopLossPoints <= 0)
   {
      Alert("[AEGIS RISK ERROR] Hard Stop Loss is mandatory! Unhedged trading prohibited.");
      return INIT_PARAMETERS_INCORRECT;
   }

   // 2. Enforce Institutional Risk Ceiling
   if(InpRiskPercent <= 0.0 || InpRiskPercent > 2.0)
   {
      Alert("[AEGIS RISK ERROR] Risk percentage must be between 0.1% and 2.0% per trade.");
      return INIT_PARAMETERS_INCORRECT;
   }

   m_trade.SetExpertMagicNumber(InpMagicNumber);
   m_trade.SetMarginMode();
   m_trade.SetTypeFillingBySymbol(_Symbol);

   // Record Day Start Equity for Emergency Drawdown Monitoring
   m_dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   m_currentDay     = iTime(_Symbol, PERIOD_D1, 0);

   // Initialize Indicator Handles
   m_fastMAHandle = iMA(_Symbol, _Period, InpFastMAPeriod, 0, MODE_EMA, PRICE_CLOSE);
   m_slowMAHandle = iMA(_Symbol, _Period, InpSlowMAPeriod, 0, MODE_EMA, PRICE_CLOSE);

   if(m_fastMAHandle == INVALID_HANDLE || m_slowMAHandle == INVALID_HANDLE)
   {
      Print("[AEGIS INIT ERROR] Failed to create indicator handles.");
      return INIT_FAILED;
   }

   PrintFormat("[AEGIS INIT] Risk Guardian EA active on %s. Day Start Equity: %.2f | Max DD: %.1f%%",
               _Symbol, m_dayStartEquity, InpMaxDailyDrawdownPercent);
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(m_fastMAHandle != INVALID_HANDLE) IndicatorRelease(m_fastMAHandle);
   if(m_slowMAHandle != INVALID_HANDLE) IndicatorRelease(m_slowMAHandle);
   PrintFormat("[AEGIS DEINIT] Risk Guardian EA stopped. Reason code: %d", reason);
}

//+------------------------------------------------------------------+
//| Emergency Circuit Breaker: Evaluate Daily Drawdown Kill-Switch   |
//+------------------------------------------------------------------+
void CheckCircuitBreaker()
{
   // Check daily rollover
   datetime today = iTime(_Symbol, PERIOD_D1, 0);
   if(today != m_currentDay)
   {
      m_currentDay            = today;
      m_dayStartEquity        = AccountInfoDouble(ACCOUNT_EQUITY);
      m_circuitBreakerTripped = false;
      PrintFormat("[AEGIS ROLLOVER] New trading day detected. Equity baseline reset to %.2f", m_dayStartEquity);
   }

   if(m_circuitBreakerTripped) return;

   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(m_dayStartEquity <= 0.0) return;

   double currentDDPercent = ((m_dayStartEquity - currentEquity) / m_dayStartEquity) * 100.0;

   // If threshold breached: Trigger Autonomous Kill-Switch
   if(currentDDPercent >= InpMaxDailyDrawdownPercent)
   {
      m_circuitBreakerTripped = true;
      Alert(StringFormat("[AEGIS CIRCUIT BREAKER TRIPPED] Max daily drawdown exceeded (%.2f%% >= %.2f%%)! Closing all trades and halting.",
                         currentDDPercent, InpMaxDailyDrawdownPercent));

      CloseAllPositions();
      CancelAllPendingOrders();
   }
}

//+------------------------------------------------------------------+
//| Close all open market positions immediately                      |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(m_position.SelectByIndex(i))
      {
         if(m_position.Magic() == InpMagicNumber)
         {
            m_trade.PositionClose(m_position.Ticket());
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Cancel all pending orders                                        |
//+------------------------------------------------------------------+
void CancelAllPendingOrders()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      if(m_order.SelectByIndex(i))
      {
         if(m_order.Magic() == InpMagicNumber)
         {
            m_trade.OrderDelete(m_order.Ticket());
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Calculate dynamic lot size from capital risk % and SL distance   |
//+------------------------------------------------------------------+
double CalculateDynamicLot(double slPoints)
{
   if(slPoints <= 0) return 0.0;

   double equity     = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskAmount = equity * (InpRiskPercent / 100.0);
   double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double point      = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

   if(point <= 0 || tickSize <= 0 || tickValue <= 0) return 0.0;

   double tickRatio  = point / tickSize;
   double pointValue = tickValue * tickRatio;

   double rawLot = riskAmount / (slPoints * pointValue);

   // Quantize to symbol requirements
   double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   double lot = MathFloor(rawLot / lotStep) * lotStep;
   if(lot < minLot) lot = 0.0; // Risk capacity insufficient for minimum lot
   if(lot > maxLot) lot = maxLot;

   return NormalizeDouble(lot, 2);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Mandatory Gate: Watchdog Circuit Breaker
   CheckCircuitBreaker();
   if(m_circuitBreakerTripped) return;

   // 2. Pre-Trade Gate: Live Spread Check
   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > InpMaxAllowedSpreadPoints)
   {
      return; // Market spread too wide; abort execution
   }

   // 3. Execution State: One Position at a Time
   if(PositionsTotal() > 0)
   {
      for(int i = 0; i < PositionsTotal(); i++)
      {
         if(m_position.SelectByIndex(i) && m_position.Magic() == InpMagicNumber)
            return; // Already in trade
      }
   }

   // 4. Signal Generation (EMA 9/21 Trend Crossover)
   double fastMA[2], slowMA[2];
   if(CopyBuffer(m_fastMAHandle, 0, 1, 2, fastMA) < 2) return;
   if(CopyBuffer(m_slowMAHandle, 0, 1, 2, slowMA) < 2) return;

   bool buySignal  = (fastMA[0] <= slowMA[0] && fastMA[1] > slowMA[1]);
   bool sellSignal = (fastMA[0] >= slowMA[0] && fastMA[1] < slowMA[1]);

   if(!buySignal && !sellSignal) return;

   // 5. Pre-Trade Gate: Dynamic Position Sizing
   double lotSize = CalculateDynamicLot((double)InpStopLossPoints);
   if(lotSize <= 0.0)
   {
      Print("[AEGIS RISK GATE] Insufficient equity to open minimum lot safely under risk rules.");
      return;
   }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

   // 6. Order Dispatch with MANDATORY Attached Hard Stop Loss
   if(buySignal)
   {
      double sl = NormalizeDouble(ask - (InpStopLossPoints * point), _Digits);
      double tp = (InpTakeProfitPoints > 0) ? NormalizeDouble(ask + (InpTakeProfitPoints * point), _Digits) : 0.0;
      m_trade.Buy(lotSize, _Symbol, ask, sl, tp, "Aegis Buy Order");
   }
   else if(sellSignal)
   {
      double sl = NormalizeDouble(bid + (InpStopLossPoints * point), _Digits);
      double tp = (InpTakeProfitPoints > 0) ? NormalizeDouble(bid - (InpTakeProfitPoints * point), _Digits) : 0.0;
      m_trade.Sell(lotSize, _Symbol, bid, sl, tp, "Aegis Sell Order");
   }
}
//+------------------------------------------------------------------+
