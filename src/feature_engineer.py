import pandas as pd
from src.graph_features import extract_graph_features

def engineer_features(df: pd.DataFrame, address: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame([{
            'tx_count': 0, 'wallet_age_days': 0, 'tx_density': 0,
            'total_value_out_eth': 0, 'outflow_per_day': 0,
            'avg_value_eth': 0, 'std_value_eth': 0, 'max_value_eth': 0,
            'unique_to_addresses': 0, 'outgoing_ratio_pct': 0,
            'outgoing_to_new_ratio_pct': 0, 'percent_large_tx': 0,
            'has_recent_spike': 0, 'interaction_degree': 0,
            'unique_counterparties': 0, 'graph_density': 0
        }])

    df = df.copy()
    df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0) / 1e18
    df['timeStamp'] = pd.to_datetime(df['timeStamp'], unit='s')
    df['is_incoming'] = df['to'].str.lower() == address.lower()

    now = pd.Timestamp.now()
    age_days = max(1, (now - df['timeStamp'].min()).days)

    tx_count = len(df)
    total_out_eth = df[~df['is_incoming']]['value'].sum()
    outgoing_ratio = (df[~df['is_incoming']].shape[0] / tx_count * 100) if tx_count > 0 else 0

    # Transfers to completely new addresses (strong draining signal)
    seen_senders = set(df['from'].str.lower()) | {address.lower()}
    outgoing_to_new = df[(~df['is_incoming']) & (~df['to'].str.lower().isin(seen_senders))].shape[0]
    outgoing_to_new_ratio = (outgoing_to_new / df[~df['is_incoming']].shape[0] * 100) if df[~df['is_incoming']].shape[0] > 0 else 0

    features = {
        'tx_count': tx_count,
        'wallet_age_days': age_days,
        'tx_density': tx_count / age_days,                    # tx per day
        'total_value_out_eth': total_out_eth,
        'outflow_per_day': total_out_eth / age_days,          # ETH per day
        'avg_value_eth': df['value'].mean(),
        'std_value_eth': df['value'].std(),
        'max_value_eth': df['value'].max(),
        'unique_to_addresses': df['to'].nunique(),
        'outgoing_ratio_pct': outgoing_ratio,
        'outgoing_to_new_ratio_pct': outgoing_to_new_ratio,
        'percent_large_tx': (df['value'] > df['value'].quantile(0.95)).mean() * 100 if not df['value'].empty else 0,
        'has_recent_spike': (df['timeStamp'] > now - pd.Timedelta(days=7)).mean() * 100,
        'early_outflow_ratio': (df[(df['timeStamp'] < df['timeStamp'].min() + pd.Timedelta(days=30)) & (~df['is_incoming'])]['value'].sum() / total_out_eth * 100) if total_out_eth > 0 else 0,
        **extract_graph_features(df, address)
    }
    return pd.DataFrame([features])