interface SignatureHistoryTableProps {
  rows: Array<{ id: string; name: string; date: string; active: boolean }>;
}

export default function SignatureHistoryTable({ rows }: SignatureHistoryTableProps) {
  return (
    <table className="fin-table">
      <thead><tr><th>Officer</th><th>Date</th><th>Active</th></tr></thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}><td>{row.name}</td><td>{row.date}</td><td>{row.active ? 'Yes' : 'No'}</td></tr>
        ))}
      </tbody>
    </table>
  );
}
