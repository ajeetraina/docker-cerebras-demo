package docker

import (
	"context"
	"fmt"
	"io"
	"runtime"

	"github.com/docker/docker/api/types/image"
	"github.com/docker/docker/client"
	"golang.org/x/sync/errgroup"
)

func (c *Client) ImageExists(ctx context.Context, name string) (bool, error) {
	_, err := c.client.ContainerInspect(ctx, name)
	if client.IsErrNotFound(err) {
		return false, nil
	}

	return err == nil, err
}

func (c *Client) PullImages(ctx context.Context, names ...string) error {
	registryAuth, err := getRegistryAuth(ctx)
	if err != nil {
		return fmt.Errorf("getting registryAuth: %w", err)
	}

	errs, ctx := errgroup.WithContext(ctx)
	errs.SetLimit(runtime.NumCPU())

	for _, name := range names {
		errs.Go(func() error {
			_, err := c.pullImage(ctx, name, registryAuth)
			return err
		})
	}

	return errs.Wait()
}

func (c *Client) PullImage(ctx context.Context, name string) error {
	registryAuth, err := getRegistryAuth(ctx)
	if err != nil {
		return fmt.Errorf("getting registryAuth: %w", err)
	}

	_, err = c.pullImage(ctx, name, registryAuth)
	return err
}

func (c *Client) pullImage(ctx context.Context, imageName, registryAuth string) (string, error) {
	inspect, err := c.client.ImageInspect(ctx, imageName)
	if err != nil && !client.IsErrNotFound(err) {
		return "", fmt.Errorf("inspecting docker image %s: %w", imageName, err)
	}

	if len(inspect.RepoDigests) > 0 {
		if inspect.RepoDigests[0] == imageName {
			return "", nil
		}
	}

	pullOptions := image.PullOptions{
		RegistryAuth: registryAuth,
	}

	response, err := c.client.ImagePull(ctx, imageName, pullOptions)
	if err != nil {
		return "", fmt.Errorf("pulling docker image %s: %w", imageName, err)
	}

	if _, err := io.Copy(io.Discard, response); err != nil {
		return "", fmt.Errorf("pulling docker image %s: %w", imageName, err)
	}

	return "", nil
}
