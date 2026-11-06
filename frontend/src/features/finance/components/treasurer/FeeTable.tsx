interface FeeTableProps {
  rows: Array<{ year: string; semester: string; amount: number; status: string }>;
}

export default function FeeTable({ rows }: FeeTableProps) {
  return (
    <table className="fin-table">
      <thead><tr><th>Year</th><th>Semester</th><th>Amount</th><th>Status</th></tr></thead>
      <tbody>
        {rows.map((row) => (
          <tr key={`${row.year}-${row.semester}`}><td>{row.year}</td><td>{row.semester}</td><td>₱{row.amount.toLocaleString()}</td><td>{row.status}</td></tr>
        ))}
      </tbody>
    </table>
  );
}
