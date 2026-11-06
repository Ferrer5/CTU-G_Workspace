interface SchoolYearTableProps {
  rows: Array<{ year: string; status: string }>; 
}

export default function SchoolYearTable({ rows }: SchoolYearTableProps) {
  return (
    <table className="fin-table">
      <thead><tr><th>Academic Year</th><th>Status</th></tr></thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.year}><td>{row.year}</td><td>{row.status}</td></tr>
        ))}
      </tbody>
    </table>
  );
}
