interface StudentsTableProps {
  rows: Array<{ school_id: string; name: string; course_code: string; year: number; section: string; status: string; balance: number }>;
}

export default function StudentsTable({ rows }: StudentsTableProps) {
  return (
    <table className="fin-table">
      <thead>
        <tr>
          <th>CTU ID</th>
          <th>Name</th>
          <th>Course</th>
          <th>Balance</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.school_id}>
            <td>{row.school_id}</td>
            <td>{row.name}</td>
            <td>{`${row.course_code}.${row.year}.${row.section}`}</td>
            <td>₱{row.balance.toLocaleString()}</td>
            <td>{row.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
