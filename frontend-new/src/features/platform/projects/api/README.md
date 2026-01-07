# Projects API Layer

**Status:** ✅ Already Implemented
**Pattern:** Uses centralized hooks from `@lumina/design-system`

## Current Implementation

The projects feature follows the recommended API integration pattern by using hooks from the design system:

```typescript
import {
  useProjects,
  useProject,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  useAddFileToProject,
  useRemoveFileFromProject,
} from '@lumina/design-system';
```

These hooks are defined in:
- `libs/shared/design-system/src/hooks/projects.ts`

## Usage

### List Projects

```typescript
function ProjectsListPage() {
  const { data, isLoading, error } = useProjects();

  if (isLoading) return <TableLoadingState rows={5} />;
  if (error) return <QueryError error={error} />;

  return <ProjectsList projects={data.items} />;
}
```

### Project Detail

```typescript
function ProjectDetailPage() {
  const { projectId } = useParams();
  const { data: project } = useProject(projectId!);

  return <ProjectDetail project={project} />;
}
```

### Create Project

```typescript
function CreateProjectModal() {
  const createProject = useCreateProject();

  const handleSubmit = async (data) => {
    await createProject.mutateAsync(data);
    // Automatically invalidates projects list
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Update Project

```typescript
function EditProjectForm({ projectId, initialData }) {
  const updateProject = useUpdateProject();

  const handleSave = async (data) => {
    await updateProject.mutateAsync({
      projectId,
      data,
    });
  };

  return <form onSubmit={handleSave}>...</form>;
}
```

### Delete Project

```typescript
function DeleteProjectButton({ projectId }) {
  const deleteProject = useDeleteProject();

  const handleDelete = async () => {
    if (confirm('Delete this project?')) {
      await deleteProject.mutateAsync(projectId);
      navigate('/workspace');
    }
  };

  return <Button onClick={handleDelete} danger>Delete</Button>;
}
```

## Feature-Specific Extensions

If you need feature-specific API logic not in the design system, add it here:

### Example: Project-Specific Query

```typescript
// queries.ts (if needed)
import { useQuery } from '@tanstack/react-query';
import { instrumentedFetch } from '@lumina/design-system';

export function useProjectAnalytics(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'analytics'],
    queryFn: async () => {
      const response = await instrumentedFetch(
        `/api/v1/projects/${projectId}/analytics`
      );
      return response.json();
    },
    enabled: !!projectId,
  });
}
```

## Why This Works

The projects feature demonstrates the **ideal API integration pattern**:

✅ **Centralized**: Common CRUD operations in design system
✅ **Reusable**: Shared across all features that use projects
✅ **Consistent**: Same error handling and loading patterns
✅ **Type-safe**: Fully typed with TypeScript
✅ **Cached**: Automatic caching and invalidation
✅ **Tested**: Design system hooks are well-tested

## When to Add Feature-Specific API Code

Add API code to this directory when:

1. **Feature-specific endpoints** - Endpoints unique to projects feature
2. **Custom transformations** - Data transformations specific to this feature
3. **Complex business logic** - Logic that doesn't belong in design system
4. **Feature flags** - Experimental features not ready for design system

## References

- Design System Hooks: `libs/shared/design-system/src/hooks/`
- API Integration Guide: `docs/API_INTEGRATION_GUIDE.md`
- Template: `src/features/_template/api/`
