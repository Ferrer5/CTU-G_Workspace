interface TransactionTableProps {
  rows: Array<{ type: string; description: string; amount: number; date: string; status?: string }>;
}

export default function TransactionTable({ rows }: TransactionTableProps) {
  return (
    <table className="fin-table">
      <thead><tr><th>Type</th><th>Description</th><th>Amount</th><th>Date</th><th>Status</th></tr></thead>
      <tbody>
        {rows.map((row, index) => (
          <tr key={`${row.type}-${row.description}-${index}`}>
            <td>{row.type}</td>
            <td>{row.description}</td>
            <td>₱{row.amount.toLocaleString()}</td>
            <td>{row.date}</td>
            <td>{row.status ?? 'Posted'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
