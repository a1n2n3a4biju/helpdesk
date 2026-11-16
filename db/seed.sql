-- Empties all tables and resets IDs to 1, so this file can be run again safely
TRUNCATE ai_feedback, ai_suggestions, ticket_activity, tickets, requesters RESTART IDENTITY CASCADE;

-- 6 employees (get IDs 1 to 6 in this order)
INSERT INTO requesters (display_name, email, department) VALUES
('Priya Raman',  'priya.raman@example.com',  'Finance'),
('Arjun Mehta',  'arjun.mehta@example.com',  'Sales'),
('Kavya Iyer',   'kavya.iyer@example.com',   'HR'),
('Rahul Nair',   'rahul.nair@example.com',   'Engineering'),
('Sneha Kapoor', 'sneha.kapoor@example.com', 'Marketing'),
('Vikram Rao',   'vikram.rao@example.com',   'Operations');

-- 7 tickets (get IDs 1 to 7 in this order)
INSERT INTO tickets (requester_id, title, description, category, priority, status, created_at, updated_at) VALUES
(1, 'Cannot connect to VPN from home', 'Since this morning the VPN client says authentication failed. I need it to reach the finance share before month-end close.', 'Network', 'High', 'In Progress', NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days'),
(2, 'Laptop battery drains very fast', 'Battery goes from 100% to 20% in about two hours, even when only using email.', 'Hardware', 'Low', 'New', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(3, 'Locked out of HR portal', 'Locked out after too many login attempts. Payroll approvals are due tomorrow.', 'Access', 'Medium', 'Resolved', NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days'),
(4, 'Excel crashes on large files', 'Excel closes without any error when I open the 40 MB quarterly report.', 'Software', 'Medium', 'In Progress', NOW() - INTERVAL '1 day', NOW() - INTERVAL '20 hours'),
(5, 'Printer on 3rd floor keeps jamming', 'The shared printer near marketing jams on almost every job. The paper tray looks fine.', 'Hardware', 'Low', 'New', NOW() - INTERVAL '6 hours', NOW() - INTERVAL '6 hours'),
(6, 'Need access to Operations dashboard', 'I joined Operations last week and need read access to the operations dashboard.', 'Access', 'Low', 'Resolved', NOW() - INTERVAL '7 days', NOW() - INTERVAL '6 days'),
(1, 'Teams calls drop after 10 minutes', 'Every Teams call disconnects after about 10 minutes. Other internet use seems fine.', 'Network', 'Medium', 'New', NOW() - INTERVAL '3 hours', NOW() - INTERVAL '3 hours');

-- History: every ticket has a 'created' row; status changes and comments follow
INSERT INTO ticket_activity (ticket_id, action, note, old_status, new_status, actor, created_at) VALUES
(1, 'created', 'Ticket raised', NULL, 'New', 'Priya Raman', NOW() - INTERVAL '3 days'),
(1, 'status_change', 'Picked up by support', 'New', 'In Progress', 'Support - Anil', NOW() - INTERVAL '2 days 20 hours'),
(1, 'comment', 'Asked user to reinstall the VPN client and retry.', NULL, NULL, 'Support - Anil', NOW() - INTERVAL '2 days'),
(2, 'created', 'Ticket raised', NULL, 'New', 'Arjun Mehta', NOW() - INTERVAL '2 days'),
(3, 'created', 'Ticket raised', NULL, 'New', 'Kavya Iyer', NOW() - INTERVAL '5 days'),
(3, 'status_change', 'Picked up by support', 'New', 'In Progress', 'Support - Meena', NOW() - INTERVAL '4 days 22 hours'),
(3, 'comment', 'Account unlocked and temporary password sent.', NULL, NULL, 'Support - Meena', NOW() - INTERVAL '4 days 2 hours'),
(3, 'status_change', 'User confirmed login works', 'In Progress', 'Resolved', 'Support - Meena', NOW() - INTERVAL '4 days'),
(4, 'created', 'Ticket raised', NULL, 'New', 'Rahul Nair', NOW() - INTERVAL '1 day'),
(4, 'status_change', 'Picked up by support', 'New', 'In Progress', 'Support - Anil', NOW() - INTERVAL '20 hours'),
(5, 'created', 'Ticket raised', NULL, 'New', 'Sneha Kapoor', NOW() - INTERVAL '6 hours'),
(6, 'created', 'Ticket raised', NULL, 'New', 'Vikram Rao', NOW() - INTERVAL '7 days'),
(6, 'status_change', 'Picked up by support', 'New', 'In Progress', 'Support - Meena', NOW() - INTERVAL '6 days 20 hours'),
(6, 'comment', 'Access granted after manager approval.', NULL, NULL, 'Support - Meena', NOW() - INTERVAL '6 days 1 hour'),
(6, 'status_change', 'Access confirmed', 'In Progress', 'Resolved', 'Support - Meena', NOW() - INTERVAL '6 days'),
(7, 'created', 'Ticket raised', NULL, 'New', 'Priya Raman', NOW() - INTERVAL '3 hours');