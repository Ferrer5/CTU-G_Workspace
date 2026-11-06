interface ExemptionPanelProps {
  students: Array<{ id: string; name: string }>; 
}

export default function ExemptionPanel({ students }: ExemptionPanelProps) {
  return (
    <div className="fin-card">
      <h3 className="dash-page-title" style={{ fontSize: '18px' }}>Exemptions</h3>
      <ul className="fin-stack">
        {students.map((student) => (
          <li key={student.id} className="fin-muted">{student.name}</li>
        ))}
      </ul>
    </div>
  );
}
