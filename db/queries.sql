-- QUERY 1: Tickets + requester details + latest status from the history table
SELECT t.id, t.title, r.display_name, r.department, latest.new_status AS latest_status, latest.created_at AS status_changed_at
FROM tickets t
JOIN requesters r ON r.id = t.requester_id
LEFT JOIN LATERAL (
    SELECT a.new_status, a.created_at
    FROM ticket_activity a
    WHERE a.ticket_id = t.id AND a.new_status IS NOT NULL
    ORDER BY a.created_at DESC
    LIMIT 1
) latest ON true
ORDER BY t.id;

-- QUERY 2: Ticket counts by status
SELECT status, COUNT(*) AS ticket_count FROM tickets GROUP BY status ORDER BY status;

-- QUERY 3: Ticket counts by priority
SELECT priority, COUNT(*) AS ticket_count FROM tickets GROUP BY priority ORDER BY priority;